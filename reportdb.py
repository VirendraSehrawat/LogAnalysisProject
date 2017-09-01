#!/usr/bin/python3

import psycopg2

dbname = "news"


def executeQuery(query):
    db = psycopg2.connect(database=dbname)
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    return result


def getMostPopularArticle():
    return executeQuery(''' select title , count(title) as num
                        from articles, log
                        where log.path = concat('/article/', articles.slug)
                        and status = '200 OK'
                        group by title
                        order by num desc LIMIT 3; ''')


def getMostArticleAuthors():
    return executeQuery(''' select name, count(name) as num
                        from authors, articles, log
                        where authors.id = articles.author
                        and log.path = concat('/article/', articles.slug)
                        group by name order by num desc;
                        ''')


def getRequestCount():
    return executeQuery('''
                    select to_char(totals.date, 'Mon DD, YYYY') as date,
                    round(100.0*error_views/total_views, 2) as error_percentage
                    from (select date(time) as date, count(*) as total_views
                    from log group by date(time)) as totals,
                    (select date(time) as date, count(*) as error_views
                    from log where status != '200 OK'
                    group by date(time)) as errors
                    where totals.date = errors.date and
                    100.0 * error_views / total_views > 1
                    order by totals.date limit 5;
                    ''')
