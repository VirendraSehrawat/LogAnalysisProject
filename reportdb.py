import psycopg2

dbname = "news"


class DataItem:
    success = 0.0
    failure = 1.0

    def evaluate_precent(self):
        print('Evaluate Percent %s %s ' % (self.success, self.failure))
        total = self.success + self.failure
        percent = self.failure * 100 / total
        return percent


def getMostPopularArticle():
    db = psycopg2.connect(database=dbname)
    cursor = db.cursor()
    cursor.execute(''' select title , count(title) as num
                        from articles, log
                        where log.path like concat('%', articles.slug)
                        group by title
                        order by num desc LIMIT 3; ''')
    result = cursor.fetchall()
    db.close()
    return result


def getMostArticleAuthors():
    db = psycopg2.connect(database=dbname)
    cursor = db.cursor()
    cursor.execute(''' select name, count(name) as num
                        from authors, articles, log
                        where authors.id = articles.author
                        and log.path like concat('%', articles.slug)
                        group by name order by num desc;
                        ''')
    result = cursor.fetchall()
    db.close()
    return result


def getRequestCount():
    db = psycopg2.connect(database=dbname)
    cursor = db.cursor()
    cursor.execute('''
                    select  DATE(time) as date,  status, count(status) as count
                    from log group by DATE(time),status;
                    ''')
    # result contains request made on a day.
    # Row contain diffrent status of the request.
    result = cursor.fetchall()
    db.close()
    dictionary = dict()

    # loop on the result to combine failed and success request
    # percentage is evaluated once value of failed
    # and successful request are known
    for date, status, count in result:
        if str(date) in dictionary:
            data_item = dictionary[str(date)]
            if status.find("200") != -1:
                data_item.success = count
            else:
                data_item.failure = count
            # remove dataitem from dictionary that have percent less than 1
            if data_item.evaluate_precent() < 1.0:
                dictionary.pop(str(date))
        else:
            data_item = DataItem()
            if status.find("200") != -1:
                data_item.success = count
            else:
                data_item.failure = count

            dictionary[str(date)] = data_item

    return dictionary
