from flask import Flask, render_template, request, redirect, abort, url_for, flash, make_response
from collections import defaultdict
import os
import re
from io import StringIO
import csv
import multiprocessing
import subprocess
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
import pg8000

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_APP_KEY', '')

from flask_login import LoginManager, login_user, logout_user, login_required
from rtbsquare_analytics.auth.users import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

users = {
    1: User(os.getenv('AUTHENTICATION_ID'), os.getenv('AUTHENTICATION_PASS')),
}

user_check = defaultdict(int)
for u in users.values():
    user_check[u.id] = u.password

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

def getSession():
    return SESSION(bind=ENGINE, autocommit=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == "POST"):
        if(request.form["id"] in user_check.keys() and request.form["password"] == user_check[request.form["id"]]):
            login_user(User(request.form["id"], request.form["password"]))
            return redirect(request.args.get('next') or url_for('index'))
        else:
            return abort(401)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    if user_id in user_check.keys():
        return User(user_id, user_check[user_id])
    else:
        return None

@app.route('/')
@login_required
def index():
    session = getSession()
    with session.connection() as conn:
        results = conn.execute("SELECT * FROM articles")
        records = results.fetchall()
        articles = list(map(lambda row:dict(zip(results.keys(), row)) , records))
        # タグ紐付け
        tags = []
        for article in articles:
            results = conn.execute("SELECT tag FROM article_tags WHERE articleId = %s;", (article['id'], ))
            records = results.fetchall()
            tags = list(map(lambda row: row[0], records))
            article['tags'] = tags
        conn.close()
    
    session.close()
    return render_template('index.html', title="index", articles=articles)

@app.route('/keywords')
@login_required
def keywords():
    articleId = request.args.get('article')
    if(articleId is None):
        return "Error: Bad request parameters."
    else:
        articleId = int(articleId)

    session = getSession()
    with session.connection() as conn:
        results = conn.execute("SELECT * FROM articles WHERE id = %s;", (articleId, ))
        record = results.fetchone()
        if(record is None):
            return "Error: articleId {} does not exists.".format(articleId)
        article = dict(record)

        results = conn.execute("SELECT tag FROM article_tags WHERE articleid = %s;", (articleId, ))
        records = results.fetchall()
        records = list(map(lambda row: dict(zip(results.keys(), row)), records))
        
        if(len(records) == 0):
            return "Error: tags are not found ... articleId = {}".format(articleId)
        tags = list(map(lambda row: row['tag'], records))
        article['tags'] = tags
        results = conn.execute("SELECT * FROM entities WHERE articleid = %s;", (articleId, ))
        records = results.fetchall()
        records = list(map(lambda row: dict(zip(results.keys(), row)), records))
        if(len(records) == 0):
            return "Error: entities are not found ... articleId = {}".format(articleId)
        entities = []
        for row in records:
            if(row['salience'] is None):
                row['salience'] = 0
            entities.append(row)
        article['entities'] = entities
    
    session.close()
    return render_template('keywords.html', title="keywords", article=article)

@app.route('/dump', methods=["POST"])
@login_required
def dump():
    if len(request.form) == 0:
        err = "Error: nothing is selected."
        return err
    else:
        f = StringIO()
        writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator="\n")

        choices = ["タイトル", "URL", "投稿日", "キーワード", "タイプ", "重要度"]
        sel_str = ""
        sel_dict = dict()
        for key in request.form.keys():
            if key in choices:
                sel_dict[key] = request.form[key]
                sel_str += request.form[key] + ", "
        sel_str = re.sub(r'(, )$', '', sel_str)

        start_date = request.form['start-date']
        end_date = request.form['end-date']

        session = getSession()
        with session.connection() as conn:
            results = conn.execute(
                "SELECT {} FROM articles INNER JOIN entities ON articles.id = entities.articleid WHERE articles.date >= '{}' AND articles.date <= '{}';"
                .format(sel_str, start_date, end_date)
                )
            records = results.fetchall()
            articles = list(map(lambda row: dict(zip(results.keys(), row)), records))
            if len(articles) < 1:
                return "指定された期間に該当する記事はありません。"

            writer.writerow(sel_dict.keys())
            for article in articles:
                writer.writerow(article.values())
        res = make_response()
        res.data = f.getvalue().encode('sjis', errors='ignore')
        f.close()
        res.headers['Content-Type'] = 'text/csv'
        res.headers['Content-Disposition'] = 'attachment; filename=keywords.csv'

        session.close()
        return res

def dailyJob():
    import datetime
    session = getSession()
    with session.connection() as conn:
        results = conn.execute('SELECT date FROM articles ORDER BY date DESC LIMIT 1;')
        record = results.fetchone()
    session.close()

    MAX_PAGE_NUM = 5
    if record is not None:
        latest = record['date']
        print("Latest article date in DATABASE: {} .".format(latest))
        try:
            end_date = datetime.date.today()
            cmd = "scrapy crawl articles -a start_date={} -a end_date={} -a crawl_start_pagenum={} -a crawl_end_pagenum={} --nolog".format(
                latest.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 1, MAX_PAGE_NUM
            )
            subprocess.check_call(cmd.split())
            import sys
            sys.path.append('../')
            from articleCrawl.languageAnalytics.analytics import analysisArticles
            analysisArticles(latest.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            print("----- Finish dailyJob -----")
        except:
            print("Error in subprocess")
    else:
        print("Error: Table articles is empty.")
    
@app.route('/crawl', methods=["GET"])
def cronCrawl():
    if request.headers.get('X-Appengine-Cron') is not None:
        p = multiprocessing.Process(target=dailyJob)
        p.start()
        return "success"
    else:
        res = make_response()
        res.status_code = 400 # bad request
        res.data = "Bad Request"
        return res

if __name__ == "__main__":
    app.config.from_pyfile('config.cfg')
    app.run(debug=True)
