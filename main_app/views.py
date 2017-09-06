from django.http import HttpResponseRedirect
from django.shortcuts import render
from . import forms
import json
from main_app import crawler, runner
from io import StringIO
from django.http import JsonResponse
import logging

logger = logging.getLogger("django")

# Create your views here.
def index(request):
    form1 = forms.statuses
    form2 = forms.search_box
    settings_dict = get_settings()
    dictionary = {'form': form1, "search": form2, "crawling":settings_dict["scanning"]}

    if request.method == 'GET':
        form1 = forms.statuses(request.GET)

    crawler.boot_db()
    returned_dict = []
    num = 1
    if form1.is_valid():
        data = form1.cleaned_data['status']
        the_array = data.split(",")
        for i in range(len(the_array)):
            the_array[i] = the_array[i].strip()
            if not the_array[i].isdigit():
                data = None
                break
            else:
                the_array[i] = int(the_array[i])
        if the_array:
            for each in the_array:
                for each2 in crawler.find_code([each]):
                    returned_dict.append({"number": num, "code": each, "url": each2})
                    num += 1
        else:
            returned_dict.append({"number": 1, "code": "null", "url": "null"})
        dictionary["status"] = returned_dict
        temp = ""
        dictionary["codes"] = []
        for each in the_array:
            temp += str(each) + ", "
            dictionary['codes'].append(each)
        dictionary["searched_for"] = temp[:len(temp) -2]
    else:
        for each2 in crawler.find_code([404]):
            returned_dict.append({"number": num, "code": 404, "url": each2})
            num += 1
        dictionary["status"] = returned_dict
        dictionary['codes'] = [404]
        dictionary["searched_for"] = 404

    return render(request, "main_app/index.html", context=dictionary)


def crawl_settings(request):
    form2 = forms.search_box
    settings_dict = get_settings()
    crawl_stats_dict = get_crawl_stats()

    dictionary = {"search": form2}
    for key, value in settings_dict.items():
        dictionary[key] = value
    for key, value in crawl_stats_dict.items():
        dictionary[key] = value
    return render(request, "main_app/crawlsettings.html", context=dictionary)


def link_details(request):
    form2 = forms.search_box
    url = request.META.get('QUERY_STRING', '')[6:]
    dictionary = {'url': url, "search": form2}
    crawler.boot_db()
    dictionary['status'] = crawler.find_code_of_url(url)
    links = crawler.find_link(url)
    returned_dict = []
    num = 1
    for each in links:
        returned_dict.append({"number": num, "status_code": crawler.find_code_of_url(each),"url": each})
        num += 1

    dictionary['status_chart'] = returned_dict

    return render(request, "main_app/linkdetails.html", context=dictionary)


def search_results(request):
    crawler.boot_db()
    form2 = forms.search_box
    url = request.GET.get('search', "")
    links = crawler.search(url)
    returned_dict = []
    num = 1
    for each in links:
        returned_dict.append({"number": num, "status_code": crawler.find_code_of_url(each),"url": each})
        num += 1
    dictionary = {"search": form2, "main_url": url, "search_results":returned_dict}
    return render(request, "main_app/searchresults.html", context=dictionary)


def update_options(request):
    settings_dict = get_settings()

    settings_dict["allowed_urls"] = [i.strip() for i in request.POST.get('allowed_urls', "").split(",")]
    settings_dict["disallowed_urls"] = [i.strip() for i in request.POST.get('disallowed_urls', "").split(",")]
    settings_dict["start_page"] = [i.strip() for i in request.POST.get('start_page', "").split(",")]
    settings_dict["recheck_redirects"] = request.POST.get('recheck_redirects', "")
    f = open('static/settings.txt', 'w')
    io = StringIO()
    json.dump(settings_dict, io)
    f.write(str(io.getvalue()))
    f.close()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def update_schedule(request):
    settings_dict = get_settings()

    settings_dict["weekly_occurance"] = request.POST.get('weekly_occurance', "")
    settings_dict["time_selection"] = request.POST.get('time_selection', "")
    settings_dict["day_of_week"] = request.POST.get('day_of_week', "")
    f = open('static/settings.txt', 'w')
    io = StringIO()
    json.dump(settings_dict, io)
    f.write(str(io.getvalue()))
    f.close()
    import crontab
    import os
    tab = crontab.CronTab(user='ccowley')
    for job in tab:
        tab.remove(job)
        tab.write()
    tab = crontab.CronTab(user='ccowley')
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    runner_dir = os.path.join(BASE_DIR, "main_app/runner.py")
    cmd = "cd {} && /usr/local/bin/python3 {} {}".format(BASE_DIR, runner_dir, BASE_DIR)
    cron_job = tab.new(cmd, comment="this is the main command")
    cron_job.minute.on(0)
    cron_job.hour.on(settings_dict['time_selection'])
    if settings_dict['weekly_occurance'] == 'thricely':
        cron_job.dow.on(1, 3, 5)
    if settings_dict['weekly_occurance'] == 'weekly':
        cron_job.dow.on(settings_dict["day_of_week"])
    tab.write()
    logger.info(tab.render())
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def start_crawl(request):
    settings_dict = get_settings()

    if not settings_dict["scanning"] or True:
        settings_dict = get_settings()
        settings_dict["scanning"] = True
        f = open('static/settings.txt', 'w')
        io = StringIO()
        json.dump(settings_dict, io)
        f.write(str(io.getvalue()))
        f.close()
        runner.run()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_settings():
    f = open('static/settings.txt', 'r').read()
    if f is not None and not f == "":
        settings_dict = json.loads(f)
    else:
        settings_dict = json.loads(open('static/backup_settings.txt', 'r').read())
        f = open('static/settings.txt', 'w')
        io = StringIO()
        json.dump(settings_dict, io)
        f.write(str(io.getvalue()))
        f.close()
    return settings_dict


def get_crawl_stats():
    f = open('static/crawl_stats.txt', 'r').read()
    if f is not None and not f == "":
        settings_dict = json.loads(f)
    else:
        return {}
    return settings_dict


def update_data(request):
    crawler.boot_db()
    the_array = [int(i.strip()) for i in str(request.GET.get('codes', None)).split(",")]
    returned_dict = {'table': []}

    num = 1
    for each in the_array:
        for each2 in crawler.find_code([each]):
            returned_dict['table'].append([num, each, each2])
            num += 1

    returned_dict['crawling'] = get_settings()['scanning']

    return JsonResponse(returned_dict)


def crawl_page(request):
    crawler.boot_db()
    returned_data = crawler.crawl_only_this_page(request.GET.get('main_url', None))
    return JsonResponse({'broken_urls': returned_data})
