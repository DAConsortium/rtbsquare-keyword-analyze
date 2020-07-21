def analysisArticles(start_date, end_date):
    from google.auth import app_engine
    from google.cloud import language_v1
    from google.cloud.language_v1 import enums, types
    from google.protobuf.json_format import MessageToJson
    import json
    import os
    import datetime
    import sqlalchemy
    from sqlalchemy.sql import text
    from sqlalchemy.orm.session import sessionmaker
    import pg8000

    client = language_v1.LanguageServiceClient()
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
    session = SESSION(bind=ENGINE, autocommit=True)
    with session.connection() as conn:
        TIMEOUT = 60.0*30.0 # timeout value in second

        with conn.begin():
            results = conn.execute("SELECT * FROM articles WHERE date > '{}' AND date <= '{}';".format(start_date, end_date))
        article_url = None
        document = None
        response = None
        entities = None

        while True:
            article = results.fetchone()
            if article is None:
                break
            
            print("Analytics: {} [{}] ".format(article['url'], article['date']))
            article_url = article['url']
            with conn.begin():
                entities_results = conn.execute("SELECT * FROM entities where article_url = '{}';".format(article_url))
                if entities_results.fetchone() is not None:
                    print("Entities already exits in entities table. ")
                    break
            
            document = types.Document(
                content = article['content'],
                type = enums.Document.Type.PLAIN_TEXT)
            response = client.analyze_entities(document=document, encoding_type="UTF8", timeout=TIMEOUT)
            response = json.loads(MessageToJson(response))
            entities = response["entities"]
            
            d = None
            for entity in entities:
                if("salience" not in entity.keys()):
                    entity['salience'] = None
                d = {"article_url": article_url, "name": entity['name'], "type": entity['type'], "salience": entity['salience']}
                with conn.begin():
                    conn.execute(
                        text("INSERT INTO entities (article_url, entity, type, salience) VALUES (:article_url, :name, :type, :salience);"), d
                    )
            
    session.close()