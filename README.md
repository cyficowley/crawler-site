This is a web crawler I wrote over Summer for work

It crawls the website and feeds all the information into a database for fast access and easy exploration of the links

Features:
* Easily veiwing all statuses on demand
* Customizable settings
* Searching for urls
* Viewing all places page is linked from (good for fixing 404s or page migrations)
* Crawling all the links on a single page (good for during development of a page) 
* Can follow links of sitemap.xml file
* Automated Crawling on a user set time interval



How to set up: (locally is exactly the same just with any version of linux)
1. get a raspberry pi (model 2 b)  (Or any sort of linux server that can run django and has the same or above specs as this pi)
2. Install raspbian https://www.raspberrypi.org/downloads/raspbian/
3. Set yourself as superuser
   1. su -
1. Install python3
   1. apt-get install build-essential libc6-dev
   2. apt-get install libncurses5-dev libncursesw5-dev libreadline6-dev
   3. apt-get install libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev
   4. apt-get install libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
   5. wget https://www.python.org/ftp/python/3.5.4/Python-3.5.4.tar.xz
   6. tar -xvf Python-3.5.4.tar.xz
   7. cd Python-3.5.4
   8. ./configure
   9. make
   10. make install
1. Install pip3
   1. apt-get install python3-pip
1. Install sqlite3
   1. apt-get install sqlite3
1. Install python sqlite
   1. apt-get install python-sqlite
1. Install git
   1. apt-get install git
1. Install django
   1. pip3 install Django
1. Install screen
   1. apt-get install screen 
1. Get files onto the server (hosted on https://github.mb-internal.com/ccowley/crawler-site)
2. Open directory
3. Install required python packages
   1. pip3 install -r requirements.txt
1. Edit /main_app/views.py
   1. Change line 134 to say the user name that you logged in with
1. Open a screen window
   1. Screen
1. Start server
   1. python3 manage.py runserver 0.0.0.0:80 (or whatever port you want)
