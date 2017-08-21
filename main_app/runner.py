import main_app.crawler as main
import time
from datetime import datetime
import json
from io import StringIO
import subprocess
import shlex


def run():
    commands = shlex.split("python3 -c 'import main_app.runner; main_app.runner.run_real()'")
    print(subprocess.Popen(commands))


def run_real():
    print("im starting Crawl")
    f = open('static/settings.txt', 'r').read()
    settings_dict = {}
    if f is not None and not f == "":
        settings_dict = json.loads(f)

    start_time = time.time()
    main.set_accepted_domains(settings_dict["allowed_urls"])
    main.set_disallowed_domains(settings_dict["disallowed_urls"])
    main.boot_db()
    main.get_redirects(settings_dict["recheck_redirects"])
    main.start_crawl(settings_dict["start_page"])

    crawl_stats = {}
    seconds = time.time() - start_time
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    crawl_stats['time_to_complete'] = "%d hours, %02d minutes and %02d seconds" % (h, m, s)

    d = datetime.now()
    current_time = d.strftime("%I:%M %p")
    current_date = d.strftime("%m/%d/%y")
    crawl_stats['full_time'] = current_date + " at " + current_time

    f = open('static/crawl_stats.txt', 'w')
    io = StringIO()
    json.dump(crawl_stats, io)
    f.write(str(io.getvalue()))
    f.close()

    f = open('static/settings.txt', 'r').read()
    settings_dict = {}
    if f is not None and not f == "":
        settings_dict = json.loads(f)
    settings_dict["scanning"] = False
    f = open('static/settings.txt', 'w')
    io = StringIO()
    json.dump(settings_dict, io)
    f.write(str(io.getvalue()))
    f.close()
