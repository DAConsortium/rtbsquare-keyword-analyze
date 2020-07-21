from web.server import dailyJob, getSession
from articleCrawl.languageAnalytics.analytics import analysisArticles
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
import pg8000
import os
import datetime
import logging
logging.basicConfig(level=logging.DEBUG, filename='./log/cron-test.log')

dbURL = sqlalchemy.engine.url.URL(
            drivername='postgres+pg8000',
            username=os.getenv('DB_USER', ''),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', '')
        )

if(os.getenv('CONNECTION_NAME') is not None):
    dbURL.query = {'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(os.getenv('CONNECTION_NAME'))}

ENGINE = sqlalchemy.create_engine(dbURL)
SESSION = sessionmaker()


def analyticsAllData(): # analytics all data in "articles" table and insert results into "entities" table
    session = getSession()
    with session.connection() as conn:
        results = conn.execute('SELECT date FROM articles ORDER BY date DESC LIMIT 1;')
        latest_date_row = results.fetchone()
        results = conn.execute('SELECT date FROM articles ORDER BY date ASC LIMIT 1;')
        oldest_date_row = results.fetchone()
    session.close()
    if latest_date_row is not None:
        latest = latest_date_row['date']
        oldest = oldest_date_row['date']
    else:
        logging.warning("DATABASE is empty.")
        exit()
    logging.info("In DATABASE, Oldest date = {}, Latest date = {}".format(oldest, latest))
    analysisArticles((oldest - datetime.timedelta(days=1)).strftime('%Y-%m-%d'), latest.strftime('%Y-%m-%d'))


if __name__ == "__main__":
    dailyJob(max_page_num=45, save_term=180, first_crawl_term=90)
    # analyticsAllData()