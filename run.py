import os

from lms_requests import app

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')

    if not os.path.exists('static/html'):
        os.makedirs('static/html')

    if not os.path.exists('static/tg_data'):
        os.makedirs('static/tg_data')

    if not os.path.exists('static/tg_data/schedule'):
        os.makedirs('static/tg_data/schedule')

    if not os.path.exists('static/tg_data/users'):
        os.makedirs('static/tg_data/users')

    from lms_requests import bot_handler
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 8080)))