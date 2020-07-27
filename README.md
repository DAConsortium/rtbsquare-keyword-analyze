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
google-auth == 1.18.0

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

## Usage(Development in Local Enviroments)

### 1. Set environment variables below
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

### 2. Install Requirements

> $ pip install -r requirements.txt

### 3. Set Database

```
$ pg_ctl start -D /usr/local/var/postgres
$ psql -U [USERNAME]
# \i sql/create_articles.sql
# \i sql/create_article_tags.sql
# \i sql/create_entities.sql
```

### 4. Run

> $ gunicorn web.server:app



## Deploy to GAE
1. make app.yaml in root folder and deploy to GAE
```
runtime: python37

entrypoint: gunicorn web.server:app --log-file -

env_variables:
  DB_NAME: "***"
  DB_USER: "***"
  DB_PASSWORD: "***"
  CONNECTION_NAME: "***"
  FLASK_APP_KEY: r"***"
  AUTHENTICATION_ID: "***"
  AUTHENTICATION_PASS: "***"
  GOOGLE_APPLICATION_CREDENTIALS: "***"

handlers:
- url: /.*
  secure: always
  redirect_http_response_code: 301
  script: auto
```

> $ gcloud app deploy app.yaml 

## Deploy Batch Process to Cloud Functions

1. make cloud functions and pubsub topic
> $ gcloud functions deploy crawl_function --source ./articleCrawl --runtime python37 --region asia-northeast1 --timeout 540 --trigger-resource crawl-trigger --trigger-event google.pubsub.topic.publish --entry-point crawl --project dac-techdev0

enviroment variables in cloud functions (set at gcp console)

```
DB_NAME=***
DB_USER=***
DB_PASSWORD=***
CONNECTION_NAME=***
GOOGLE_APPLICATION_CREDENTIALS=***
SCRAPY_SETTINGS_MODULE="settings"
MAX_PAGE_NUM=5
SAVE_TERM=180
FIRST_CRAWL_TERM=30
```

2. make cloud scheduler to kick pubsub

## LICENCE
Reference [LICENCE.txt](LICENSE.txt)