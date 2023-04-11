# WORKLOG POLICE, OPEN UP

This bot for reminding to write worklog.

### Helm values
| Variable                 | Value        | Description                                                                                             |
|--------------------------|--------------|---------------------------------------------------------------------------------------------------------|
| slack.thread.enabled     | 0/1          | Enable to write messages in thread                                                                      |
| slack.thread.msg_to_find | STRING       | If thread enabled this variable need to contain message content to find it and start or continue thread |
| slac.token               | STRING       | Slack bot token                                                                                         |
| slac.channel.dev         | STRING       | Slack dev channel                                                                                       |
| slac.channel.prod        | STRING       | Slack prod channel                                                                                      |
| jira.domain              | STRING       | Jira domain                                                                                             |
| jira.user                | STRING       | Jira user email                                                                                         |
| jira.token               | STRING       | Jira user token                                                                                         |
| jira.time_to_trigger     | INTEGER      | If worklog is less than this time (in minutes) - user will be tagged in message(s)                      |
| jira.users               | STRING ARRAY | User metadata and if need to tag, example in values                                                     |
| debug                    | 0/1          | Write messages to prod or dev channel                                                                   |
| dry_run                  | 0/1          | If need to see how bot will gather worklog time                                                         |
| cronjob.enabled          | true/false   | Enable or disable cronjob                                                                               |
| cronjob.image            | STRING       | Image of cronjob                                                                                        |
| cronjob.tag              | STRING       | Tag of image                                                                                            |
| cronjob.imagePullPolicy  | STRING       | Image pull policy                                                                                       |
| cronjob.schedule         | STRING       | Cron format schedule, examples in values                                                                |



