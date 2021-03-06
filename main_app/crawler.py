import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse
import requests
import sqlite3
import json
from io import StringIO
from fuzzywuzzy import process


class HrefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            dict_attrs = dict(attrs)
            if dict_attrs.get('href'):
                self.hrefs.add(dict_attrs['href'])

    def error(self, message):
        pass


visited_links = {}
looking_for = set()
already_in_database = {}
accepted_domains = set()
disallowed_domains = set()
redirects = {}
local_links_with_params = {}
headers = {"User-Agent": "cyrus-bot", 'From': 'cyficowley@gmail.com'}


def boot_db():
    # Run every time, starts the database up
    global con
    con = sqlite3.connect('./db.sqlite3')
    global cursor
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS main_app_sites (url text, list text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS main_app_statuses (url text, code text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS main_app_redirects (old_url text, new_url text)''')
    con.commit()


def rebuild_db():
    # is run by start_crawl, rewrites the sites database after it has been entirely crawled
    execute("DELETE FROM main_app_sites")
    for key, value in visited_links.items():
        io = StringIO()
        json.dump(value,io)
        execute("INSERT INTO main_app_sites (url, list) VALUES ('{}','{}')".format(key,io.getvalue()))
        con.commit()


def get_all():
    # returns all the things from the sites database
    execute("SELECT * FROM main_app_sites")
    rows = cursor.fetchall()
    return rows


def add_redirect(url, new_url):
    # adds a redirect to the database as long as not already in, or a redirect to self
    if url.endswith('/'):
        url = url[:len(url)-1]
    if new_url.endswith('/'):
        new_url = new_url[:len(new_url)-1]
    if (url not in redirects or not redirects[url] == new_url) and not url == new_url:
        redirects[url] = new_url
        if execute("SELECT EXISTS(SELECT 1 FROM main_app_redirects WHERE old_url='{}' LIMIT 1)".format(url)).fetchone()[0] == 1:
            execute("UPDATE main_app_redirects SET new_url='{}' WHERE old_url='{}'".format(new_url, url))
        else:
            execute("INSERT INTO main_app_redirects (old_url, new_url) VALUES ('{}','{}')".format(url, new_url))
        con.commit()


def get_redirects(recheck_redirects=True):
    # run at start, reads database and makes sure that all are still valid redirects
    execute("SELECT * FROM main_app_redirects")
    rows = cursor.fetchall()
    for i in range(0, len(rows)):
        redirects[rows[i][2]] = rows[i][1]

    if recheck_redirects:
        redirects_copy = dict(redirects)
        for key, value in redirects_copy.items():
            try:
                code = requests.get(key, stream = True, headers=headers)
                new_url = code.url
                if not (code.status_code == 404 and key in value):
                    if new_url.endswith("/"):
                        new_url = new_url[:len(new_url) -1]
                    if not new_url == value:
                        if new_url == key:
                            del redirects[key]
                            execute("DELETE FROM main_app_redirects WHERE old_url = '{}'".format(key))
                            con.commit()
                        else:
                            add_redirect(key, new_url)
                    elif key == value:
                        del redirects[key]
                        execute("DELETE FROM main_app_redirects WHERE old_url = '{}'".format(key))
                        con.commit()

            except requests.ConnectionError as e:
                # print("\nlink {} dropped this error, {}".format(key, e))
                pass
            except requests.exceptions.Timeout as e:
                # print("\nlink {} timed out".format(key))
                pass
            except requests.exceptions.InvalidSchema as e:
                # print("\nwait this broke {}".format(key))
                pass


def check_old(codes=[404]):
    # checks all old links in database, to see if any have been moved
    set_looking_for(codes)
    # print("\nRechecking links in database \n\n\n\n")
    urls = get_all
    for group in urls:
        status_change(group[0], group[1])


def set_looking_for(input):
    # sets what error codes will be printed
    pass
    for each in input:
        looking_for.add(each)


def get_local_links(html, url):
    # gets the local links on a page, sometimes using quereys.  There may be problems here with weirdly formatted links
    hrefs = set()
    parser = HrefParser()
    try:
        parser.feed(html)
    except TypeError as e:
        # print("\nError in parsing url {}, {}".format(url, e))
        pass
    for link in parser.hrefs:
        parsed = urlparse(link, allow_fragments=True)
        if link.startswith('/') and not link.startswith('//'):
            components = urlparse(url)
            new = "{}://{}{}".format(components.scheme, components.netloc, parsed.path)
            if new.endswith("/"):
                new = new[:len(new)-1]
            if not parsed.query == "":
                local_links_with_params[new] = "{}://{}{}?{}".format(components.scheme, components.netloc, parsed.path, parsed.query)
            hrefs.add(new)
        else:
            scheme = parsed.scheme

            if scheme == "":
                scheme = urlparse(url).scheme
            new = "{}://{}{}".format(scheme, parsed.netloc, parsed.path)
            if new.endswith("/"):
                new = new[:len(new)-1]
            if not parsed.query == "":
                local_links_with_params[new] = "{}://{}{}?{}".format(scheme, parsed.netloc, parsed.path, parsed.query)
            hrefs.add(new)
    return hrefs


def set_accepted_domains(accepted_domain):
    # sets which domains will be completely searched through, run at start
    for each in accepted_domain:
        accepted_domains.add(each)


def set_disallowed_domains(accepted_domain):
    # sets which domains will not be looked at, run at start
    for each in accepted_domain:
        disallowed_domains.add(each)


def start_crawl(start_urls, codes=[404]):
    # starts the crawler, run at beginning to re-crawl the entire website
    set_looking_for(codes)
    execute("DELETE FROM main_app_statuses")
    # print("\n\n\n\n\nCrawling website, starting at {}".format(start_urls[0]))
    for each in start_urls:
        crawl_site(each, "")
    rebuild_db()


def crawl_only_this_page(url, codes=[404]):
    # only crawls a single web page looking for broken links.  Perfect for making sure dev page is working
    html = get_content(url, "")
    broke_links = []
    used_links = []
    if html is not None:
        for link in get_local_links(html, url):
            if link.endswith("/"):
                link = link[:len(link) -1]
            if link in redirects:
                link = redirects[link]
            if link not in broke_links and link not in used_links:
                used_links.append(link)
                try:
                    code = requests.get(link, stream = True, timeout=3, headers=headers)
                    if not code.url == link:
                        add_redirect(link, code.url)
                    if code.status_code in codes:
                        if link in local_links_with_params:
                            link = local_links_with_params[link]
                            code = requests.get(link, stream = True, headers=headers)
                        if code.status_code in codes:
                            broke_links.append(link)
                except requests.ConnectionError as e:
                    # print("\nlink {} : {}".format(url, e))
                    pass
                except requests.exceptions.Timeout as e:
                    # print("\nlink {}  timed out".format(url))
                    pass
                except requests.exceptions.InvalidSchema as e:
                    pass
                except requests.exceptions.MissingSchema as e:
                    # print(link)
                    pass
    return broke_links


def crawl_site(url, old_url):
    # main crawl runner, is started by start_crawl
    if url.endswith("/"):
        url = url[:len(url) - 1]
    if url in redirects:
        url = redirects[url]
    if not url.startswith("#"):
        if url not in visited_links:
            domain = urlparse(url).netloc
            if domain is not '' and len(url) > 1 and domain not in disallowed_domains:
                visited_links[url] = [old_url]
                if domain in accepted_domains:
                    html = get_content(url, old_url)
                    if url in redirects:
                        url = redirects[url]
                    if url.endswith(".xml"):
                        parse_xml(html, url)
                    if html is not None:
                        for link in get_local_links(html, url):
                            crawl_site(link, url)
                else:
                    check_status(url, old_url)
        else:
            if url in local_links_with_params:
                del local_links_with_params[url]
            if old_url not in visited_links[url]:
                visited_links[url].append(old_url)


def parse_xml(html, url):
    # parses an xml document so it can be scanned
    root = ET.fromstring(html)
    for i in range(0, len(root)):
        if root[i][0].text.endswith("/"):
            root[i][0].text = root[i][0].text[:len(root[i][0].text) -1]
        if root[i][0].text in redirects:
            root[i][0].text = redirects[root[i][0].text]
        crawl_site(root[i][0].text, url)


def get_content(url, old_url):
    # gets the content of an html file, checks for stuff
    try:
        if ".jpg" not in url and ".pdf" not in url and "downloads" not in url:
            code = requests.get(url, stream = True, headers=headers)
        else:
            code = requests.head(url, headers=headers)
        if code.is_redirect:
            add_redirect(url, code.url)
        if isinstance(code.status_code, int):
            update_urls_code(url, code.status_code)
        if code.status_code in looking_for:
            previous_url = url
            if url in local_links_with_params:
                url = local_links_with_params[url]
                code = requests.get(url, stream = True, headers=headers)
                del local_links_with_params[previous_url]
            if code.status_code in looking_for:
                print("\nthis url {} from {} is broken with code {}".format(url, old_url, code.status_code))
            else:
                add_redirect(previous_url, url)
                update_urls_code(url, code.status_code)
                return code.text
        elif ".jpg" not in url and ".pdf" not in url and "downloads" not in url:
            if not code.url == url:
                add_redirect(url, code.url)
            return code.text
        else:
            if url in local_links_with_params:
                del local_links_with_params[url]
    except requests.ConnectionError as e:
        # print("\nlink {} : {}".format(url, e))
        pass
    except requests.exceptions.Timeout as e:
        # print("\nlink {}  timed out".format(url))
        pass


def check_status(url, old_url):
    # checks status without seatching behond that
    try:
        code = requests.get(url, stream = True, timeout=3, headers=headers)
        if isinstance(code.status_code, int):
            update_urls_code(url, code.status_code)
        if old_url not in visited_links[url]:
            visited_links[url].append(old_url)
        if code.status_code in looking_for:
            previous_url = url
            if url in local_links_with_params:
                url = local_links_with_params[url]
                code = requests.get(url, stream = True, headers=headers)
                del local_links_with_params[previous_url]
            if code.status_code in looking_for:
                # print("\nthis url {} from {} is broken with code {}".format(url, old_url, code.status_code))
                pass
            else:
                add_redirect(previous_url, url)
                update_urls_code(url, code.status_code)
        else:
            if url in local_links_with_params:
                del local_links_with_params[url]
        return code.status_code
    except requests.ConnectionError as e:
        # print("\nlink {} : {}".format(url,  e))
        pass
    except requests.exceptions.Timeout as e:
        # print("\nlink {}  timed out".format(url))
        pass
    except requests.exceptions.InvalidSchema as e:
        del visited_links[url]
    except UnicodeError as e:
        # print("\nunicode screwed up on link {} from {}".format(url, old_url))
        pass


def status_change(url, old_urls):
    # checks for a change in the status code without adding it to the visited_links, is for rechecking everything fast
    already_in_database[url] = json.loads(old_urls)
    try:
        code = requests.get(url, stream = True, timeout=3, headers=headers)
        if isinstance(code.status_code, int):
            update_urls_code(url, code.status_code)
        if code.status_code in looking_for:
            print("\nthis link {} is returning {}".format(url, code.status_code))
        else:
            update_urls_code(url, code.status_code)
        return code.status_code
    except requests.ConnectionError as e:
        # print("\nlink {} dropped this error, {}".format(url, e))
        pass
    except requests.exceptions.Timeout as e:
        # print("\nlink {} timed out".format(url))
        pass
    except requests.exceptions.InvalidSchema as e:
        # print("\nwait this broke {}".format(url))
        pass


def update_urls_code(url, code):
    # adds to the statuses database the new status of a url
    if execute("SELECT EXISTS(SELECT 1 FROM main_app_statuses WHERE url='{}' LIMIT 1)".format(url)).fetchone()[0] == 1:
        execute("UPDATE main_app_statuses SET code={} WHERE url='{}'".format(code,url))
    else:
        execute("INSERT INTO main_app_statuses (url, code) VALUES ('{}','{}')".format(url,code))
    con.commit()


def find_code(requested_codes):
    # checks for all codes that have a certain status
    sql_query = "SELECT * FROM main_app_statuses WHERE "
    for num in requested_codes:
        sql_query += "code = {} OR ".format(num)
    sql_query = sql_query[:len(sql_query)-4]
    execute(sql_query)
    rows = cursor.fetchall()
    returned_urls = set()
    for i in range(0, len(rows)):
        returned_urls.add(rows[i][1])
    return returned_urls


def find_code_of_url(url):
    # finds the status of the inputted url
    if url.endswith("/"):
        url = url[:len(url) - 1]
    sql_query = "SELECT * FROM main_app_statuses WHERE url = '{}'".format(url)
    execute(sql_query)
    rows = cursor.fetchall()
    if rows == []:
        return None
    status = rows[0][2]
    return status


def find_link(url):
    # returns all pages linking to a certain link
    if url.endswith("/"):
        url = url[:len(url) - 1]
    execute("SELECT * FROM main_app_sites WHERE url = '{}'".format(url))
    temp = cursor.fetchall()
    if not temp:
        return "No Matches"
    temp = json.loads(temp[0][2])
    return temp


def search(url):
    execute("SELECT * FROM main_app_statuses")
    temp = cursor.fetchall()
    urls = [i[1] for i in temp]
    return [i[0] for i in process.extract(url, urls, limit=10)]


def execute(the_input):
    try:
        return cursor.execute(the_input)
    except sqlite3.ProgrammingError as e:
        boot_db()
        return cursor.execute(the_input)
