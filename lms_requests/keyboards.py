from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def generate_schedule_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Dushanba", callback_data="monday"),
        InlineKeyboardButton("Seshanba", callback_data="tuesday"),
        InlineKeyboardButton("Chorshanba", callback_data="wednesday"),
        InlineKeyboardButton("Payshanba", callback_data="thursday"),
        InlineKeyboardButton("Juma", callback_data="friday"),
        InlineKeyboardButton("Shanba", callback_data="saturday"),

    )
    return markup