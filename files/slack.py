# xapp-1-A05L3QH639V-5695462729973-f5305cd6d37287f1083028e67690a4c42c2a57f3bf90304eb2186a66f4973f52
from datetime import datetime, timedelta
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
import logging
import json
import dates
import config as configuration
import logging
import report
import table
import permissions
import sqlite

import os

version = 0.2

SLACK_BOT_TOKEN = ""
SLACK_APP_TOKEN = ""
client = WebClient(token=SLACK_BOT_TOKEN)
app = App(token=SLACK_BOT_TOKEN)

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
roles = json.loads(open("./roles.json", "r").read())

@app.command("/add_dayoff")
def add_dayoff(body, say, respond, ack):
    logging.info(f"Command /add_dayoff {body['text']}")
    logging.info(f"By @{body['user_name']}")
    logging.info(body)
    ack()
    config = configuration.get(logging)
    permission = permissions.get(body, roles, config)
    logging.info(f'Permissions: {permission}')
    if permission:
        config = configuration.update(body, config, permission, "add_dayoff")
        if config[1]:
            dayoff = config[3]
            try:
                days = dates.parse(config[0])
            except:
                respond("Bad date format, example: 2023-08-31")
            logging.info(f'Days: {days[0]}:{days[-1]}')
            for user in config[0]['users']:
                # pass
                sqlite.add_dayoff(days, logging, user, dayoff)
            respond("Successfully added dayoff(s)")
        else:
            respond(config[2])
    else:
        respond("You are not authorized!")


@app.command("/make_report")
def make_report(body, say, respond, ack):
    pass

# NOT RELEASED
@app.command("/make_table")
def make_table(body, say, respond, ack):
    logging.info(f"Command /make_report {body['text']}")
    logging.info(f"By @{body['user_name']}")
    logging.info(body)
    ack()
    config = configuration.get(logging)
    permission = permissions.get(body, roles, config)
    logging.info(f'Permissions: {permission}')
    if permission:
        config = configuration.update(body, config, permission, "make_report_table")
        if config[1]:
            try:
                days = dates.parse(config[0])
            except:
                respond("Bad date format, example: 2023-08-31")
            logging.info(f'Days: {days[0]}:{days[-1]}')
            if len(days) > permission['make_report_table']['limit']:
                respond("You tried to make table in range over your limit")
                return
            init_msg = say(text="Started getting work logs. It can take some time.")

            finish_table = table.make(config[0], logging, days)
            client.chat_delete(
                channel=init_msg['channel'],
                ts=init_msg['ts']
            )
            client.files_upload_v2(
                channels=body['channel_id'],
                initial_comment="Generated new report table:",
                file=finish_table,
            )
            os.remove(finish_table)
        else:
            respond(config[2])
    else:
        respond("You are not authorized!")

@app.command("/make_report_table")
def make_report_table(body, say, respond, ack):
    logging.info(f"Command /make_report_table {body['text']}")
    logging.info(f"By @{body['user_name']}")
    logging.info(body)
    ack()
    config = configuration.get(logging)
    permission = permissions.get(body, roles, config)
    logging.info(f'Permissions: {permission}')
    if permission:
        config = configuration.update(body, config, permission, "make_report_table")
        if config[1]:
            try:
                days = dates.parse(config[0])
            except:
                respond("Bad date format, example: 2023-08-31")
            logging.info(f'Days: {days[0]}:{days[-1]}')
            if len(days) > permission['make_report_table']['limit']:
                respond("You tried to make table in range over your limit")
                return
            init_msg = say(text="Started getting work logs. It can take some time.")

            report.make(config[0], logging, days)
            finish_table = table.make(config[0], logging, days)
            client.chat_delete(
                channel=init_msg['channel'],
                ts=init_msg['ts']
            )
            client.files_upload_v2(
                channels=body['channel_id'],
                initial_comment="Generated new report table:",
                file=finish_table,
            )
            os.remove(finish_table)
        else:
            respond(config[2])
    else:
        respond("You are not authorized!")

@app.command("/help")
def help(body, say, respond, ack):
    ack()
    header = '''Hello, this is WorkLogger Bot!
Here you can make report by date(s), table in human-readable format and add day off!
Command use example:'''
    add_deyoff_help = f'''
*Add a day off*
`/add_dayoff <type of dayoff> <user> <date>`
Arguments:
    *type of dayoff*: can be `1` or `0.5` (0.5 - is a half-dayoff) 
    • optional, by default - 1
    *user*: can be `all` or `@user` for for which dayoff will be set
    • optional, by default - you
    • only `admins` can use this argument
    *date*: date for set dayoff, format:
    • single date: `{datetime.today().strftime("%Y-%m-%d")}`
    • multiple dates: `{datetime.today().strftime("%Y-%m-%d")},{(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")}`
    • range: `{datetime.today().strftime("%Y-%m-%d")}:{(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")}`
    • optional, by default - today
Examples:
```/add_dayoff```
```/add_dayoff 1```
```/add_dayoff 1 @user```
```/add_dayoff 1 all```
```/add_dayoff 1 {datetime.today().strftime("%Y-%m-%d")}```
```/add_dayoff 1 @user {datetime.today().strftime("%Y-%m-%d")}```
```/add_dayoff 0.5 @user {datetime.today().strftime("%Y-%m-%d")},{(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")}```
```/add_dayoff 1 all {datetime.today().strftime("%Y-%m-%d")}:{(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")}```'''

    make_report_table_help = f'''
*Make report table*
`/make_report_table <user> <date>`
Arguments:
    *user*: can be `all` or `@user` for for which dayoff will be set
    • optional, by default - you
    • only `admins` can use this argument
    *date*: date for set dayoff, format:
    • single date: `{datetime.today().strftime("%Y-%m-%d")}`
    • multiple dates: `{datetime.today().strftime("%Y-%m-%d")},{(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")}`
    • range: `{datetime.today().strftime("%Y-%m-%d")}:{(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")}`
    • optional, by default - today
Examples:
```/make_report_table```
```/make_report_table @user```
```/make_report_table {datetime.today().strftime("%Y-%m-%d")}```
```/make_report_table @user {datetime.today().strftime("%Y-%m-%d")}```
```/make_report_table all {datetime.today().strftime("%Y-%m-%d")},{(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")}```
```/make_report_table all {datetime.today().strftime("%Y-%m-%d")}:{(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")}```'''
    respond(header+add_deyoff_help+make_report_table_help)

# @app.event("message")
# def handle_message_events(body, logger, say):



if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()