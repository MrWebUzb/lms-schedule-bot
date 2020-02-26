import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from lms_requests import bot
from lms_requests.globals import admin
from lms_requests.lms import get_random_agent, get_lms_session

cron = BlockingScheduler()


@cron.scheduled_job('interval', minutes=15)
def checking_cookie():
    url = 'https://lms.tuit.uz/dashboard/news'
    csrf_token = 'eyJpdiI6ImdGY0h6bW16cGswY0FMRnlJSDlyR3c9PSIsInZhbHVlIjoiMU82eWc0eEhCWFVrS29RNXVMZHhlTW5sdmlIaXBsbDh3dUJpVmsyNjZOV3AzWVVxVlRCUUVVMjFOS2J6bnZySCIsIm1hYyI6ImZhNGE2YmJmNWUyYTM0Y2U3NmRhYWMxOTRiNDdhODdjMTc0YjUxM2U5MGFiOGQ3MTFiMDM4NjhlMDA5ODcyNmMifQ%3D%3D'
    user_agent = get_random_agent()
    client = requests.Session()
    client.cookies.set(name='tuit_lms_session', value=get_lms_session())
    headers = {'User-Agent': user_agent}
    client.get(url, headers=headers)

    if 'XSRF-TOKEN' in client.cookies:
        csrf_token = client.cookies['XSRF-TOKEN']
    else:
        csrf_token = csrf_token

    client.cookies.set(name='XSRF-TOKEN', value=csrf_token)
    response = client.get(url, headers=headers)

    if response.status_code == 200:
        bot.send_message(chat_id=admin, text='Cookie uchun so\'rov jo\'natildi. Hammasi joyida.')
    else:
        bot.send_message(chat_id=admin, text='Cookie eskirdi yoki boshqa xatolik yuz berdi. Tekshirib ko\'ring va yangi cookie ni saqlang.')


cron.start()