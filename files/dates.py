from datetime import datetime, timedelta

def parse(config):
    # print(config)
    if ":" in config["jira"]["worklog_date"]:
        dates = config["jira"]["worklog_date"].split(":")
        if dates[0]:
            start_date = datetime.strptime(dates[0], "%Y-%m-%d")
        else:
            start_date = datetime.today()
        if dates[1]:
            end_date = datetime.strptime(dates[1], "%Y-%m-%d")
        else:
            end_date = datetime.today()
    else:
        start_date = datetime.strptime(config["jira"]["worklog_date"], "%Y-%m-%d")
        end_date = start_date
    delta_dates = end_date - start_date
    days = []
    for i in range(delta_dates.days + 1):
        days.append((start_date + timedelta(days=i)).strftime("%Y-%m-%d"))
    return days