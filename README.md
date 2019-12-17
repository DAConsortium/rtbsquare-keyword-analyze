# Rtbsquare-App


## Overview
Crawl articles from resource page and analysis contents of each articles by Google Natural Language API.

Resource: https://rtbsquare.work/
Google Natural language API : https://cloud.google.com/natural-language/docs/

## Requirements
```
Scrapy == 1.7.4
google-cloud-language == 1.3.0
google-api-python-client == 1.7.11
google-auth-httplib2 == 0.0.3
google-auth == 1.6.3

gunicorn == 20.0.0
sqlalchemy == 1.3.7
pg8000 == 1.13.2
Flask == 1.0.2
Flask-Login == 0.4.1
google-cloud-language == 1.3.0
```

## Develop Environment
- postgresql
- python3.7.3

## Usage

1. Set environment variables below
```
export DB_NAME = ***
export DB_USER = ***
export DB_PASSWORD = ***
export FLASK_APP_KEY = ***
export GOOGLE_APPLICATION_CREDENTIALS = ***
```
note. 
- GOOGLE_APPLICATION_CREDENTIALS is path to credential file of natural language api.
Google Natural language API : https://cloud.google.com/natural-language/docs/

- The FLASK_APP_KEY is needed to keep the client-side sessions secure.
You can generate some random key as below
```
>>> import os
>>> os.urandom(24)
'\xfd{H\xe5<\x95\xf9\xe3\……………xa2\xa0\x9fR"\xa1\xa8'
```

## LICENCE
Reference [LICENCE.txt](LICENSE.txt)