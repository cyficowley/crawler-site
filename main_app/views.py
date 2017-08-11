from django.shortcuts import render


# Create your views here.
def index(response):
    dictionary = {'inserted_value': 'Test'}
    return render(response, "main_app/index.html", context=dictionary)


def crawl_settings(response):
    dictionary = {'inserted_value': 'Test'}
    return render(response, "main_app/crawlsettings.html", context=dictionary)


def link_details(response):
    dictionary = {'inserted_value': 'Test'}
    return render(response, "main_app/linkdetails.html", context=dictionary)


def search_results(response):
    dictionary = {'inserted_value': 'Test'}
    return render(response, "main_app/searchresults.html", context=dictionary)
