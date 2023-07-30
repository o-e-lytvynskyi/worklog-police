import sqlite3

def init(logging):
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
    if not cur.fetchall():
        cur.execute("CREATE TABLE reports(datetime, slack_id, user_email, worklogs, time_logged, UNIQUE(datetime, slack_id, user_email) ON CONFLICT REPLACE)")
        con.commit()
        logging.info('Created DB "reports"')
    else:
        logging.info('DB "reports" already exist')



def insert(datas, datatime, logging):
    con = sqlite3.connect("db")
    cur = con.cursor()
    for data in datas:
        to_write = (datatime, data['slack_id'], data['user_email'], data['worklogs'], data['time_logged'])
        cur.execute(
            "INSERT INTO reports ('datetime', 'slack_id', 'user_email', 'worklogs', 'time_logged') VALUES (?, ?, ?, ?, ?)",
            to_write
        )
    con.commit()
    logging.info(f'Wrote to DB:\n{to_write}')
def select():
    pass
# init()