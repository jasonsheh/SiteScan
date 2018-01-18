# SiteScan


***
## Install

#### requirement
+ celery
+ redis
+ chromedriver
+

change the path in setting.py to your own path

run `python3 ./database/database.py` to create database

***
## Run

### run as program

run `python3 ./sitescan.py -d [domain]` to collect infomation of that domain

run `python3 ./web.py` to open the web interface

### run as web service

run `celery -A cel worker -l info --config=celeryconfig`

run `python3 ./web.py` to open the web interface

***

## console
![menu](https://raw.githubusercontent.com/jasonsheh/SiteScan/master/doc/console.png)

## Web

![subdomain](https://raw.githubusercontent.com/jasonsheh/SiteScan/master/doc/subdomain.png)

![port](https://raw.githubusercontent.com/jasonsheh/SiteScan/master/doc/port.png)
