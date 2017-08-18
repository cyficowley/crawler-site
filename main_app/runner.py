import main_app.crawler as main
import time
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
    print("--- %s seconds ---" % (time.time() - start_time))

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
