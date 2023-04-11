import requests
from requests.auth import HTTPBasicAuth
import json
import os
import datetime
import logging

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)

config = json.loads(open("/proj/config.json", "r").read())

if config['jira']['token']:
    jira_token = config['jira']['token']
else:
    jira_token = os.environ['jira_api_token']

if config['slack']['token']:
    slack_token = config['slack']['token']
else:
    slack_token = os.environ['slack_api_token']

def write_resp(resp):
    f = open("response.json", "w")
    f.write(str(resp))
    f.close()

def get_worklog(auth, headers, user, today):
    time_spent=0
    issue_url = f"https://{config['jira']['domain']}/rest/api/3/search?jql=worklogAuthor={user['id']} AND worklogDate={today}"
    response = requests.request("GET", issue_url, headers=headers, auth=auth)
    issues = json.loads(response.text)
    for issue in issues['issues']:
        worklog_url = f"https://{config['jira']['domain']}/rest/api/3/issue/{issue['key']}/worklog"
        response = requests.request("GET", worklog_url, headers=headers, auth=auth)
        worklogs = json.loads(response.text)
        for worklog in worklogs['worklogs']:
            worklog_time = datetime.datetime.strptime(worklog['created'][:22], "%Y-%m-%dT%H:%M:%S.%f")
            worklog_time = worklog_time.strftime("%Y-%m-%d")
            if datetime.datetime.strptime(worklog_time, "%Y-%m-%d") == datetime.datetime.strptime(today, "%Y-%m-%d"):
                if worklog['author']['accountId'] == user['id']:
                    time_spent += worklog['timeSpentSeconds']
    worklog_count = len(issues['issues'])
    logging.info(f'Worklogs by {user["email"]}: {worklog_count}, time logged: {time_spent/60/60}h')
    return {"slack_id": user['slack_id'], "worklogs": worklog_count, "time_logged": time_spent/60}

def main():
    report = []
    if config['jira']['worklog_date']:
        today = config['jira']['worklog_date']
    else:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
    logging.info(f'Starting getting worklogs for {today}')

    for user in config['users']:
        if user['active']:
            report.append(
                get_worklog(
                    HTTPBasicAuth(config['jira']['user'], jira_token),
                    {"Accept": "application/json"},
                    user,
                    today
                )
            )
    bad_guys = ''
    for rep in report:
        if rep['time_logged'] < config['jira']['time_to_trigger']:
            bad_guys += f'• <@{rep["slack_id"]}>\n'
    if bad_guys:
        head=':alert:*ATTENTION, IT IS WORKLOGPOLICE*:alert:\nAnd i know, that these guy(s) didn\'t write a worklog today or logged less than 8 hours:\n'
        message = head+bad_guys
        react = 'alert'
    else:
        message = ':aaw_yeah:*ATTENTION, IT IS WORKLOGPOLICE*:aaw_yeah:\nWow, today all work logs have been written'
        react = 'aaw_yeah'
    logging.info(f"Message to send:\n{message}")
    slack(message, react)


def slack(message, react):
    send_resp=''
    if config['debug']:
        channel_id = config['slack']['channel']['dev']
    else:
        channel_id = config['slack']['channel']['prod']

    if config['slack']['thread']['enabled']:
        find_resp = requests.request("POST", f"https://slack.com/api/conversations.history", headers={"Content-type": "application/x-www-form-urlencoded"},
                                     data={"channel": channel_id, "token": slack_token})
        find_resp = json.loads(find_resp.text)
        if "messages" in find_resp:
            for msg in find_resp['messages']:
                if msg['text'] == config['slack']['thread']['msg_to_find']:
                    ts = datetime.datetime.fromtimestamp(float(msg['ts']))
                    if ts.day == datetime.datetime.today().day and not config['dry_run']:
                        if 'reply_count' in msg and not config['slack']['repeat']:
                            if msg['reply_count'] != 0:
                                if_i_wrote = requests.request("POST", f"https://slack.com/api/conversations.replies", headers={"Content-type": "application/x-www-form-urlencoded"},
                                                              data={"channel": channel_id, "token": slack_token, "ts": msg['thread_ts']})
                                if_i_wrote = json.loads(if_i_wrote.text)
                                for rep_msg in if_i_wrote['messages']:

                                    if 'user' in rep_msg:
                                        if rep_msg['user'] == config['slack']['bot_id']:
                                            send_resp = requests.request("POST", f"https://slack.com/api/chat.update", headers={"Content-type": "application/x-www-form-urlencoded"},
                                                                         data={"channel": channel_id, "token": slack_token, "ts": rep_msg['ts'], "text": message, "link_names": 1})
                                            send_resp = json.loads(send_resp.text)

                                            logging.info(f'Successfully updated message with ts: {rep_msg["ts"]} in channel {channel_id} under thread with ts: {msg["ts"]}')
                        if not send_resp:
                            send_resp = requests.request("POST", f"https://slack.com/api/chat.postMessage", headers={"Content-type": "application/x-www-form-urlencoded"},
                                                         data={"channel": channel_id, "token": slack_token, "thread_ts": msg['ts'], "text": message, "link_names": 1})
                            send_resp = json.loads(send_resp.text)
                            logging.info(f'Successfully sent message in channel {channel_id} under thread with ts: {msg["ts"]}')
        if not send_resp and not config['dry_run']:
            logging.warning(f'Can\'t find reminder message!')
    elif not config['dry_run']:
        if_i_wrote = requests.request("POST", f"https://slack.com/api/conversations.history", headers={"Content-type": "application/x-www-form-urlencoded"},
                                      data={"channel": channel_id, "token": slack_token})
        if_i_wrote = json.loads(if_i_wrote.text)
        if "messages" in if_i_wrote and not config['slack']['repeat']:
            for msg in if_i_wrote['messages']:
                ts = datetime.datetime.fromtimestamp(float(msg['ts']))
                if ts.day == datetime.datetime.today().day and not config['dry_run']:
                    if msg['user'] == config['slack']['bot_id']:
                        send_resp = requests.request("POST", f"https://slack.com/api/chat.update", headers={"Content-type": "application/x-www-form-urlencoded"},
                                                     data={"channel": channel_id, "token": slack_token, "ts": msg['ts'], "text": message, "link_names": 1})
                        send_resp = json.loads(send_resp.text)
                        logging.info(f'Successfully updated message with ts: {msg["ts"]} in channel {channel_id}')
                        break
        if not send_resp:
            send_resp = requests.request("POST", f"https://slack.com/api/chat.postMessage", headers={"Content-type": "application/x-www-form-urlencoded"},
                                         data={"channel": channel_id, "token": slack_token, "text": message, "link_names": 1})
            send_resp = json.loads(send_resp.text)
    if send_resp:
        react_resp = requests.request("POST", f"https://slack.com/api/reactions.get", headers={"Content-type": "application/x-www-form-urlencoded"},
                                      data={"channel": channel_id, "token": slack_token, "timestamp": send_resp["ts"]})
        react_resp = json.loads(react_resp.text)
        if 'reactions' in react_resp['message']:
            for ex_react in react_resp['message']['reactions']:
                if config['slack']['bot_id'] in ex_react['users']:
                    requests.request("POST", f"https://slack.com/api/reactions.remove", headers={"Content-type": "application/x-www-form-urlencoded"},
                                     data={"channel": channel_id, "token": slack_token, "timestamp": send_resp["ts"], "name": ex_react['name']})
        requests.request("POST", f"https://slack.com/api/reactions.add", headers={"Content-type": "application/x-www-form-urlencoded"},
                         data={"channel": channel_id, "token": slack_token, "timestamp": send_resp["ts"], "name": react})
    elif config['dry_run']:
        logging.info(f'Dry-run mode enabled, message wasn\'t send')
    else:
        logging.error(f'Unknown')
main()
