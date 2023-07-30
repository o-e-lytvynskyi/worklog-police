import json
import os
import datetime
import sqlite

local = True
def get(logging):
    if local:
        config = json.loads(open("./config_local.json", "r").read())
        config["db"] = "sqlite"
        sqlite.init(logging)
    else:
        config = json.loads(open("/proj/config.json", "r").read())
        config["db"] = "postgresql"

    if not config['jira']['token']:
        config['jira']['token'] = os.environ['jira_api_token']

    if not config['slack']['token']:
        config['slack']['token'] = os.environ['slack_api_token']

    if not config['jira']['worklog_date']:
        config['jira']['worklog_date'] = datetime.datetime.now().strftime('%Y-%m-%d')

    return config