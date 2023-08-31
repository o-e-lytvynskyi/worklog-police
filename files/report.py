from requests.auth import HTTPBasicAuth
import datetime
import worklog
import sqlite
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

def make(config, logging, days):
    report = []
    with logging_redirect_tqdm():
        for day in tqdm(days):
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
    logging.info("Report completed")