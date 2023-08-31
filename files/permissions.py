def get(body, roles, config):
    for user in config['users']:
        if body['user_id'] == user['slack_id']:
            return roles[user['role']]
    return False