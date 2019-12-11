import os
import sqlalchemy
from sqlalchemy.sql import text
from sqlalchemy.orm.session import sessionmaker
import pg8000

class ArticlecrawlPipeline(object):

    def __init__(self, db_name, db_user):
        self.db_name = db_name
        self.db_user = db_user
        self.engine = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername='postgres+pg8000',
                username=os.getenv('DB_USER', ''),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', ''),
                query={
                    'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(os.getenv('CONNECTION_NAME', ''))
                }
            )
        )
        self.mksession = sessionmaker()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_name = os.getenv('DB_NAME', ''),
            db_user = os.getenv('DB_USER', '')
        )
    
    def open_spider(self, spider):
        self.session = self.mksession(bind=self.engine, autocommit=True)
        self.conn = self.session.connection()
    
    def close_spider(self, spider):
        self.session.close()
    
    def process_item(self, item, spider):
        last_id = None
        try:
            with self.conn.begin():
                results = self.conn.execute("SELECT * FROM articles WHERE url = '{}'".format(item['url']))
                record = results.fetchone()
            if record is None:
                with self.conn.begin():
                    self.conn.execute(
                        text("INSERT INTO articles (url, date, title, content) VALUES(:url, to_date(:date, 'YYYY/MM/DD'), :title, :content);"),
                        item
                    )
                    results = self.conn.execute("SELECT last_value from articles_id_seq;")
                last_id = results.fetchone()['last_value']
                d = None
                for tag in item['tags']:
                    d = {"lastid": last_id, "tag": tag}
                    with self.conn.begin():
                        self.conn.execute(
                            text("INSERT INTO article_tags (articleId, tag) VALUES(:lastid, :tag);"), d
                        )
                print("[INFO] new item {} ".format(item)) # for log of GAE
            else:
                print("[WARNING] item already exists: {}".format(item))
            return item
        except Exception as e:
            print("Error in pipeline.")
            print(e)
            pass