import telebot
from telebot import types
from databases_methods.admins_methods import update_admin_info as update_admin_info_db, get_admin

bot = telebot.TeleBot('7903231812:AAE0zim_gbjgysiiXmHmRsG_P0s33PlxkZs')


# клавиатурка
def admin_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Изменить список учащихся', callback_data = 'edit_list_of_group'))
    markup.add(types.InlineKeyboardButton('Изменить информацию о себе', callback_data = 'admin_edit_info'))
    markup.add(
        types.InlineKeyboardButton('Просмотр доступных работ', callback_data = 'admin_task'))
    return markup


def setup_admin_handlers(bot):
    @bot.callback_query_handler(func = lambda callback: callback.data in ['admin_edit_info'])
    def update_admin_info(callback):
        admin = get_admin(callback.message.chat.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Изменить имя', callback_data = 'update_admin_name'))
        markup.add(types.InlineKeyboardButton('Изменить свой список групп', callback_data = 'update_admin_group'))
        bot.send_message(callback.message.chat.id, f"Ваше имя: {admin[2]}.\n"
                                                   f"Ваши группы: {admin[3]}.\n"
                                                   f"Выберите, что вы хотите изменить:",
                         reply_markup = markup)

    @bot.callback_query_handler(func = lambda callback: callback.data in ['update_admin_name', 'update_admin_group'])
    def handle_update_request(callback):
        if callback.data == 'update_admin_name':
            bot.send_message(callback.message.chat.id, f"Введите новое имя.")
            bot.register_next_step_handler(callback.message, process_update_name)
        if callback.data == 'update_admin_group':
            bot.send_message(callback.message.chat.id, f"Введите новый список групп.")
            bot.register_next_step_handler(callback.message, process_update_group)

    def process_update_name(message):
        new_name = message.text
        if update_admin_info_db(message.from_user.id, new_full_name=new_name):
            print("all ok, we changed name")
            admin = get_admin(message.from_user.id)
            bot.send_message(message.chat.id, "Информация изменена.\n"
                                              f"Ваше имя: {admin[2]}\n"
                                              f"Ваша группа: {admin[3]}",
                             reply_markup = admin_keyboard())  # добавить вывод информации
        else:
            print("we didn't(")
            bot.send_message(message.chat.id, "Не удалось изменить информацию.")

    def process_update_group(message):
        new_group = message.text
        if update_admin_info_db(message.from_user.id, new_groups_of_students=new_group):
            admin = get_admin(message.from_user.id)
            bot.send_message(message.chat.id, "Информация изменена.\n"
                                              f"Ваше имя: {admin[2]}\n"
                                              f"Ваша группа: {admin[3]}",
                             reply_markup = admin_keyboard())
        else:
            bot.send_message(message.chat.id, "Не удалось изменить информацию.")
