import os

from lms_requests import lms
from lms_requests.globals import bot, admin

from lms_requests.keyboards import generate_schedule_keyboard
from lms_requests.lms import save_user_by_id, save_lms_session


@bot.message_handler(commands='start')
def start(message):
    if message.chat.id == admin:
        bot.send_message(chat_id=message.chat.id,
                         text='Admin siz /session va /users buyruqlaridan foydalana olasiz.')
    login = lms.get_user_login_by_id(message.chat.id)
    if not login:
        bot.send_message(chat_id=message.chat.id,
                         text="Assalomu alaykum. Botdan foydalanishdan avval quyidagi [Foydalanish shartlari](https://telegra.ph/Foydalanish-shartlari-02-24) bilan tanishib chiqing.",
                         parse_mode='markdown')
    else:
        bot.send_message(message.chat.id, "Siz avvalroq ro'yxatdan o'tgansiz. /schedule buyrug'idan foydalaning.")


@bot.message_handler(commands='users')
def users(message):
    if message.chat.id == admin:
        DIR = 'tg_data/users'
        registered_users = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        bot.send_message(message.chat.id, f"Botdan ro'yxatdan o'tganlar soni: {registered_users}.")
    else:
        return


@bot.message_handler(commands='terms')
def terms(message):
    bot.send_message(chat_id=message.chat.id,
                     text="Assalomu alaykum. Botdan foydalanishdan avval quyidagi [Foydalanish shartlari](https://telegra.ph/Foydalanish-shartlari-02-24) bilan tanishib chiqing.",
                     parse_mode='markdown')


@bot.message_handler(commands='reg')
def registration(message):
    login = lms.get_user_login_by_id(message.chat.id)
    if not login:
        text = "Botdan foydalanish uchun lms.tuit.uz saytidagi login va parolingizni\n```\nlogin * parol\n```\nko'rinishida kiriting."
        msg = bot.send_message(message.chat.id, text=text, parse_mode='markdown')
        bot.register_next_step_handler(msg, lms_registration)
    else:
        bot.send_message(message.chat.id, "Siz avvalroq ro'yxatdan o'tgansiz. /schedule buyrug'idan foydalaning.")


def lms_registration(message):
    data = message.text.split('*')

    if len(data) != 2:
        msg = bot.send_message(message.chat.id,
                               '🤦‍♂️🤦🏼‍♂️\nNoto\'g\'ri ko\'rinishda login hamda parolni kiritdingiz.\nIltimos qayta urinib ko\'ring!')
        bot.register_next_step_handler(msg, lms_registration)

    else:
        login = data[0].strip()
        password = data[1].strip()
        id = message.chat.id
        if not save_user_by_id(login, password, id):
            bot.send_message(message.chat.id, 'Xatolik yuz berdi. Qayta urinib ko\'ring.')
        else:
            bot.send_message(message.chat.id,
                             '🥳🥳🥳\nSiz muvaffaqiyatli ro\'yxatdan o\'tdingiz. Dars jadvalingizni bilish uchun /schedule buyrug\'idan foydalaning.')


@bot.message_handler(commands=["schedule"])
def schedule(message):
    keyboard = generate_schedule_keyboard()
    login = lms.get_user_login_by_id(message.chat.id)
    if login is not False:
        user = message.from_user.first_name
        bot.send_message(message.chat.id, f"{user} ning dars jadvali", reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f"Iltimos avval ro'yxatdan o'ting yoki shartlar bilan tanishing:\n/reg yoki /start")


@bot.callback_query_handler(func=lambda query: query.data in [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday'
])
def get_user_schedule(query):
    if query.message:
        key = query.data
        login = lms.get_user_login_by_id(query.message.chat.id)
        if login is not False:
            days = {
                'monday': "Dushanba",
                'tuesday': "Seshanba",
                'wednesday': "Chorshanba",
                'thursday': "Payshanba",
                'friday': "Juma",
                'saturday': "Shanba"
            }
            schedule = lms.get_table(login)
            schedule = schedule[key]["subjects"]
            schedule_text = f"📆{days[key]} dars jadvali\n"
            schedule_text += f"08:30 - 09:50 📕 {schedule[0]}\n"
            schedule_text += f"10:00 - 11:20 📕 {schedule[1]}\n"
            schedule_text += f"11:30 - 12:50 📕 {schedule[2]}\n"
            schedule_text += f"13:00 - 14:20 📕 {schedule[3]}\n"
            schedule_text += f"14:30 - 15:50 📕 {schedule[4]}\n"
            schedule_text += f"16:00 - 17:20 📕 {schedule[5]}\n"
            schedule_text += f"17:30 - 18:50 📕 {schedule[6]}"

            keyboard = generate_schedule_keyboard()

            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                  text=schedule_text, reply_markup=keyboard)
            bot.answer_callback_query(query.id, None)
        else:
            bot.send_message(chat_id=query.message.chat.id,
                             text=f"Iltimos avval ro'yxatdan o'ting yoki shartlar bilan tanishing:\n/reg yoki /start")
            bot.answer_callback_query(query.id, None)


'''ADMINISTRATION'''


@bot.message_handler(commands=['session'])
def set_session(message):
    if message.chat.id == admin:
        msg = bot.send_message(message.chat.id, 'lms_tuit_session ni menga yuboring:')
        bot.register_next_step_handler(msg, save_session)
    else:
        return


def save_session(message):
    session = message.text
    if save_lms_session(session):
        bot.send_message(message.chat.id, 'Muvaffaqiyatli saqlandi.')
    else:
        msg = bot.send_message(message.chat.id, 'Ma\'lumotni saqlashda xatolik. Iltimos qayta urinib ko\'ring.')
        bot.register_next_step_handler(msg, save_session)
