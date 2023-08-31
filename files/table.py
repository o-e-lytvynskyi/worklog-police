import sqlite
import pandas as pd
import random
import string

def make(config, logging, days):
    filename = f'/tmp/{"".join(random.choices(string.ascii_lowercase + string.digits, k=7))}.csv'

    #TODO: select all data from table with timerange
    table = []
    st_sn_count = 0
    count_active_users = 0
    for user in config['users']:
        if user['active']:
            count_active_users += 1
            sub_table = [user["email"]]
            for day in days:
                sql_query = sqlite.select(user, day)
                if not sql_query[6]:
                    sub_table.append(round(sql_query[5]/60, 2))
                else:
                    if sql_query[6] == 1:
                        sub_table.append(f"{round(sql_query[5]/60, 2)}|day off")
                    elif sql_query[6] == 1.1:
                        sub_table.append(f"{round(sql_query[5]/60, 2)}|day off(st-sn)")
                        st_sn_count += 1
                    elif sql_query[6] == 0.5:
                        sub_table.append(f"{round(sql_query[5]/60, 2)}|half day off")
            table.append(sub_table)
    headers = ["users"] + days
    df = pd.DataFrame(table, columns=headers)
    time_norm = (len(days)) * 8
    st_sn_count = st_sn_count / count_active_users
    time_norm = time_norm - (st_sn_count * 8)
    sum_time = []
    minus_time = []
    # print(len(days))
    # print(df)
    for i in range(count_active_users):
        # print(i)
        # print(df.iloc[i].values.flatten().tolist()[1:])
        row = df.iloc[i].values.flatten().tolist()[1:]
        user_sum_time = 0
        user_minus_time = 0
        for time in row:
            if isinstance(time, str):
                if time.split('|')[1] == "day off":
                    user_minus_time += 8
                elif time.split('|')[1] == "half day off":
                    user_minus_time += 4
                time = time.split('|')[0]
            user_sum_time += float(time)

        sum_time.append(round(user_sum_time, 2))
        minus_time.append(round(user_minus_time, 2))
    total_time = [x + y for x, y in zip(sum_time, minus_time)]
    delta = []
    for time in total_time:
        delta.append(round(time - time_norm, 2))
    print(total_time)
    print(sum_time)
    df[f"Total working time"] = sum_time
    df["Time balance"] = delta

    df.to_csv(filename, index=False)
    logging.info("Table completed")
    return filename


