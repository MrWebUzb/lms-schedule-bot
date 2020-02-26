import json
import os

import requests
import random
from bs4 import BeautifulSoup

from lms_requests import users
from lms_requests.globals import schedule_url


def get_random_agent():
    agents = {
        'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
        'apple_ipad': 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
        'apple_iphone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        'samsung_phone': 'Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G570Y Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/44.0.2403.133 Mobile Safari/537.36',
        'htc': 'Mozilla/5.0 (Linux; Android 7.0; HTC 10 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36',
    }

    key = random.choice(list(agents.keys()))

    return agents[key]


def get(url, stud_info_id, lms_session):
    client = requests.Session()
    url = f'{schedule_url}/{stud_info_id}'

    if os.path.isfile(f'static/html/{stud_info_id}.html'):
        try:
            with open(f'static/html/{stud_info_id}.html', 'rb') as f:
                content = f.read()
                return 200, content
        except Exception as e:
            print(str(e))
    else:
        print('Sending request')
        csrf_token = 'eyJpdiI6ImdGY0h6bW16cGswY0FMRnlJSDlyR3c9PSIsInZhbHVlIjoiMU82eWc0eEhCWFVrS29RNXVMZHhlTW5sdmlIaXBsbDh3dUJpVmsyNjZOV3AzWVVxVlRCUUVVMjFOS2J6bnZySCIsIm1hYyI6ImZhNGE2YmJmNWUyYTM0Y2U3NmRhYWMxOTRiNDdhODdjMTc0YjUxM2U5MGFiOGQ3MTFiMDM4NjhlMDA5ODcyNmMifQ%3D%3D'
        user_agent = get_random_agent()

        client.cookies.set(name='tuit_lms_session', value=lms_session)
        # client.proxies = {'http': 'http://162.252.146.183:8291', 'https': 'https://162.252.146.183:8291'}
        headers = {'User-Agent': user_agent}
        client.get(url, headers=headers)

        if 'XSRF-TOKEN' in client.cookies:
            csrf_token = client.cookies['XSRF-TOKEN']
        else:
            csrf_token = csrf_token

        client.cookies.set(name='XSRF-TOKEN', value=csrf_token)
        response = client.get(url, headers=headers)

        try:
            with open(f'static/html/{stud_info_id}.html', 'w+') as f:
                content = response.content
                f.write(str(content))
        except Exception as e:
            print(str(e))

        return response.status_code, response.content


def get_name(login):
    stud_info_id = users.get_user_id(login)
    if stud_info_id is not False:
        response_code, content = get(schedule_url, stud_info_id, get_lms_session())
        if response_code == 200:
            soup = BeautifulSoup(content, 'html.parser')
            user_name = soup.find('h3')
            user_name = user_name.string.encode('utf-8')
            user_name = user_name.decode('utf-8')
            user_name = user_name[len('Dars jadvali - '):]
            return user_name
        else:
            return False
    else:
        return False


def get_table(login):
    stud_info_id = users.get_user_id(login)
    time_table = {
        "monday": {
            "subjects": []
        },
        "tuesday": {
            "subjects": []
        },
        "wednesday": {
            "subjects": []
        },
        "thursday": {
            "subjects": []
        },
        "friday": {
            "subjects": []
        },
        "saturday": {
            "subjects": []
        }
    }
    if stud_info_id is not False:
        file_path = f'static/tg_data/schedule/{stud_info_id}.json'
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as fr:
                time_table = json.load(fr)
                return time_table
        else:
            response_code, content = get(schedule_url, stud_info_id, get_lms_session())
            if response_code == 200:
                soup = BeautifulSoup(content, 'html.parser')
                table = soup.find('table', class_="table")
                table_body = table.tbody

                for row in table_body.find_all('tr'):
                    count = 1
                    for day in time_table.keys():
                        if count == 7:
                            count = 1
                        subject = row.find_all('td')[count].contents[0][2:]
                        subject = subject.lstrip()
                        subject = subject.rstrip()
                        if subject == "":
                            subject = "Bekorchilik 🤩"
                        time_table[day]["subjects"].append(subject)
                        count += 1

                save_time_table(time_table, stud_info_id)
                return time_table
            else:
                return False
    else:
        return False


def save_time_table(table, stud_info_id):
    try:
        file_path = f"static/tg_data/schedule/{stud_info_id}.json"
        with open(file_path, 'w+') as fw:
            json.dump(table, fw)

            return True
    except Exception as e:
        print(str(e))

    return False


def get_lms_session():
    try:
        file_path = "static/lms_session.txt"
        with open(file_path, 'rt', encoding='utf-8') as f:
            lms_session = f.read()
            return lms_session
    except Exception as e:
        print(str(e))

    return False


def get_user_login_by_id(id):
    file_path = f"static/tg_data/users/{id}.json"
    login = False
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as fr:
            data = json.load(fr)
            login = data["user"]["login"]

    return login


def save_user_by_id(login, password, id):
    file_path = f"static/tg_data/users/{id}.json"
    try:
        with open(file_path, 'w+') as fw:
            json.dump({
                "user": {
                    "login": login,
                    "password": password
                }
            }, fw)
            return True
    except Exception as e:
        print(str(e))

    return False


def save_lms_session(session):
    file_path = 'static/lms_session.txt'
    try:
        with open(file_path, 'w') as wf:
            wf.write(session)
            return True
    except Exception as e:
        print(str(e))

    return False