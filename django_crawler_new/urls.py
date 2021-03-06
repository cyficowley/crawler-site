"""django_crawler_new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from main_app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name="index"),
    url(r'^crawl-settings/', views.crawl_settings, name="crawl-settings"),
    url(r'^link-details/', views.link_details, name="link-details"),
    url(r'^search-results/', views.search_results, name="search-results"),
    url(r'^update-options/', views.update_options, name="update-options"),
    url(r'^update-schedule/', views.update_schedule, name="update-schedule"),
    url(r'^start-crawl/', views.start_crawl, name="start-crawl"),
    url(r'^ajax/update-data/$', views.update_data, name='update_data'),
    url(r'^ajax/crawl-page/$', views.crawl_page, name='crawl_page'),
]
