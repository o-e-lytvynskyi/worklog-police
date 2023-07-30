from requests.auth import HTTPBasicAuth
import worklog
import sqlite
from datetime import datetime, timedelta
def make(config, logging):
    report = []
    if "/" in config["jira"]["worklog_date"]:
        dates = config["jira"]["worklog_date"].split("/")
        start_date = datetime.strptime(dates[0], "%Y-%m-%d")
        end_date = datetime.strptime(dates[1], "%Y-%m-%d")
    else:
        start_date = datetime.strptime(config["jira"]["worklog_date"], "%Y-%m-%d")
        end_date = start_date
    delta_dates = end_date - start_date


    # print(delta_dates)
    for i in range(delta_dates.days + 1):
        day = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for user in config['users']:
            if user['active']:
                report.append(
                    worklog.get(
                        HTTPBasicAuth(config['jira']['user'], config['jira']['token']),
                        {"Accept": "application/json"},
                        config,
                        user,
                        logging,
                        day
                    )
                )
        if config["db"] == "sqlite":
            sqlite.insert(report, day, logging)
        elif config["db"] == "postgresql":
            pass
    # print(report)
