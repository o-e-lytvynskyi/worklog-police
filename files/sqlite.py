import sqlite3

def init(logging):
    con = sqlite3.connect("/tmp/db")
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
    if not cur.fetchall():
        cur.execute("CREATE TABLE reports(datetime, slack_id, user_email, worklogs, issues, time_logged, dayoff, UNIQUE(datetime, slack_id, user_email) ON CONFLICT REPLACE)")
        cur.execute("CREATE TABLE dayoff(datetime, slack_id, user_email, dayoff, UNIQUE(datetime, slack_id, user_email) ON CONFLICT REPLACE)")
        con.commit()
        logging.info('Created DB "reports"')
    else:
        logging.info('DB "reports" already exist')

def insert(datas, datatime, logging):
    con = sqlite3.connect("/tmp/db")
    cur = con.cursor()
    for data in datas:
        is_add_dayoff = cur.execute(
            "SELECT dayoff FROM dayoff WHERE slack_id=? AND datetime=?",
            (data['slack_id'], datatime)
        ).fetchone()
        if is_add_dayoff:
            if is_add_dayoff[0]:
                #IDK what i have done here
                to_write = (datatime, data['slack_id'], data['user_email'], data['worklogs'], str(data['issues']), data['time_logged'], float(is_add_dayoff[0]))
            else:
                to_write = (datatime, data['slack_id'], data['user_email'], data['worklogs'], str(data['issues']), data['time_logged'], float(data['dayoff']))
        else:
            to_write = (datatime, data['slack_id'], data['user_email'], data['worklogs'], str(data['issues']), data['time_logged'], float(data['dayoff']))
        cur.execute(
            "INSERT INTO reports ('datetime', 'slack_id', 'user_email', 'worklogs', 'issues', 'time_logged', 'dayoff') VALUES (?, ?, ?, ?, ?, ?, ?)",
            to_write
        )
        con.commit()

def add_dayoff(datatimes, logging, user, dayoff):
    con = sqlite3.connect("/tmp/db")
    cur = con.cursor()
    for datatime in datatimes:
        cur.execute(
            "insert into dayoff (datetime, slack_id, user_email, dayoff) VALUES (?, ?, ?, ?)",
            (datatime, user["slack_id"], user["email"], dayoff)
        )
        is_exist = cur.execute(
            "SELECT * FROM reports WHERE slack_id=? AND datetime=?",
            (user["slack_id"], datatime)
        ).fetchone()

        if is_exist:
            is_exist = list(is_exist)
            is_exist[-1:] = [1]
            cur.execute(
                "INSERT INTO reports ('datetime', 'slack_id', 'user_email', 'worklogs', 'issues', 'time_logged', 'dayoff') VALUES (?, ?, ?, ?, ?, ?, ?)",
                is_exist
            )
    con.commit()

def select(user, day):
    con = sqlite3.connect("/tmp/db")
    cur = con.cursor()
    select = cur.execute("SELECT * FROM reports WHERE slack_id=? AND datetime=?", (user["slack_id"], day)).fetchone()
    return select
# init()