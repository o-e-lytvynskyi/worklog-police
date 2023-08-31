import json
import requests
import datetime

def get(auth, headers, config, user, logging, date):
    time_spent = 0
    issue_url = f"https://{config['jira']['domain']}/rest/api/3/search?jql=worklogAuthor={user['id']} AND worklogDate={date}"
    response = requests.request("GET", issue_url, headers=headers, auth=auth)
    issues = json.loads(response.text)
    issues_wl = []
    for issue in issues['issues']:
        issues_wl.append(issue['key'])
        worklog_url = f"https://{config['jira']['domain']}/rest/api/3/issue/{issue['key']}/worklog"
        response = requests.request("GET", worklog_url, headers=headers, auth=auth)
        worklogs = json.loads(response.text)
        for worklog in worklogs['worklogs']:
            worklog_time = datetime.datetime.strptime(worklog['created'][:22], "%Y-%m-%dT%H:%M:%S.%f")
            worklog_time = worklog_time.strftime("%Y-%m-%d")

            if datetime.datetime.strptime(worklog_time, "%Y-%m-%d") == datetime.datetime.strptime(date, "%Y-%m-%d"):
                if worklog['author']['accountId'] == user['id']:
                    time_spent += worklog['timeSpentSeconds']
    worklog_count = len(issues['issues'])
    logging.info(f'Worklogs by {user["email"]}: {worklog_count}, time logged: {time_spent/60/60}h')
    if datetime.datetime.strptime(date, "%Y-%m-%d").weekday() >= 5:
        is_dayoff = 1.1
    else:
        is_dayoff = 0
    return {"slack_id": user['slack_id'], "user_email": user["email"], "worklogs": worklog_count, "time_logged": time_spent/60, "issues": issues_wl, "dayoff": is_dayoff}