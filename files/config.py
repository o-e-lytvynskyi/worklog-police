import json
import os
from datetime import datetime
import sqlite

local = False
def get(logging):
    if local:
        config = json.loads(open("./config_local.json", "r").read())
        config["db"] = "sqlite"
        sqlite.init(logging)
    else:
        config = json.loads(open("/proj/config.json", "r").read())
        # config["db"] = "postgresql"
        config["db"] = "sqlite"
        sqlite.init(logging)

    if not config['jira']['token']:
        config['jira']['token'] = os.environ['jira_api_token']

    if not config['slack']['token']:
        config['slack']['token'] = os.environ['slack_api_token']

    if not config['jira']['worklog_date']:
        config['jira']['worklog_date'] = datetime.now().strftime('%Y-%m-%d')

    return config

def old_update(body, config, permission, action):
    if body['text']:
        args = body['text'].split(' ')
        if '@' in args[0]:
            if permission[action]['other']:
                for user in config['users']:
                    if user['slack_name'] == args[0][1:]:
                        config['users'] = [{
                            "email": user['email'],
                            "id": user['id'],
                            "slack_id": user['slack_id'],
                            "slack_name": user['slack_name'],
                            "active": user['active']
                        }]
                        break
                if len(args) >= 2:
                    days = args[1]
                else:
                    days = datetime.today().strftime("%Y-%m-%d")
            else:
                return config, 0, "You don't have permissions to get worklogs for another user"
        elif args[0] == "all":
            if permission[action]['other']:
                days = args[1]
            else:
                return config, 0, "You don't have permissions to get worklogs for another user"
        else:
            days = args[0]
    else:
        days = datetime.today().strftime("%Y-%m-%d")

    config["jira"]["worklog_date"] = days
    return config, 1, "All is ok"

def get_user(args, config):
    for user in config['users']:
        if user['slack_name'] == args[1:]:
            return [{
                "email": user['email'],
                "id": user['id'],
                "slack_id": user['slack_id'],
                "slack_name": user['slack_name'],
                "active": user['active']
            }]
    return False

def update(body, config, permission, action):
    day_off = 1
    if body['text']:
        args = body['text'].split(' ')
        if len(args) == 1:
            if '@' in args[0] or args[0] == "all":
                # /make_report_table @user
                # /add_dayoff @user
                if permission[action]['other']:
                    if '@' in args[0]:
                        config['users'] = get_user(args[0], config)
                        if not config['users']:
                            return config, 0, "Unknown username"
                    days = datetime.today().strftime("%Y-%m-%d")
                else:
                    return config, 0, f"You don't have permissions to use action {action} for another user"
            else:
                try:
                    # /add_dayoff 1|0.5
                    day_off = float(args[0])
                    config['users'] = get_user(f"@{body['user_name']}", config)
                    days = datetime.today().strftime("%Y-%m-%d")
                except:
                    # /make_report_table date
                    # /add_dayoff date
                    config['users'] = get_user(f"@{body['user_name']}", config)
                    days = args[0]
        elif len(args) == 2:
            if '@' in args[0] or args[0] == "all":
                # /make_report_table @user date
                # /add_dayoff @user date
                # /add_dayoff all date
                if permission[action]['other']:
                    if '@' in args[0]:
                        config['users'] = get_user(args[0], config)
                        if not config['users']:
                            return config, 0, "Unknown username"
                    days = args[1]
                else:
                    return config, 0, f"You don't have permissions to use action {action} for another user"
            else:
                try:
                    # /add_dayoff 1|0.5 @user
                    # /add_dayoff 1|0.5 all
                    day_off = float(args[0])
                    if action == "add_dayoff":
                        if '@' in args[1] or args[1] == "all":
                            if permission[action]['other']:
                                if '@' in args[1]:
                                    config['users'] = get_user(args[1], config)
                                    if not config['users']:
                                        return config, 0, "Unknown username"
                                days = datetime.today().strftime("%Y-%m-%d")
                            else:
                                return config, 0, f"You don't have permissions to use action {action} for another user"
                        else:
                            # make /add_dayoff 1|0.5 date
                            # TODO:users can't use it
                            try:
                                day_off = float(args[0])
                                days = args[1]
                                config['users'] = get_user(f"@{body['user_name']}", config)
                            except:
                                return config, 0, "Bad arguments"
                    else:
                        return config, 0, "Bad arguments"
                except:
                    return config, 0, "Bad arguments"
        elif len(args) == 3:
            # /add_dayoff 1|0.5 @user date
            if '@' in args[1] or args[1] == "all":
                if permission[action]['other']:
                    try:
                        day_off = float(args[0])
                        if '@' in args[1]:
                            config['users'] = get_user(args[1], config)
                        print(config['users'])
                        if not config['users']:
                            return config, 0, "Unknown username"
                        days = args[2]
                    except:
                        return config, 0, "Bad arguments"
                else:
                    return config, 0, f"You don't have permissions to use action {action} for another user"
            else:
                return config, 0, "Bad arguments"
        elif len(args) > 3:
            return config, 0, "Bad arguments"
    else:
        # /make_report_table
        # /add_dayoff
        config['users'] = get_user(f"@{body['user_name']}", config)
        days = datetime.today().strftime("%Y-%m-%d")

    config["jira"]["worklog_date"] = days
    # print(config)
    if action == "add_dayoff":
        return config, 1, "All is ok", day_off
    elif action == "make_report_table":
        return config, 1, "All is ok"