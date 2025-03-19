import telebot
from telebot import types
from databases_methods.students_methods import update_student_info, get_student

bot = telebot.TeleBot('7903231812:AAE0zim_gbjgysiiXmHmRsG_P0s33PlxkZs')


# клавиатурка
def students_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Изменить информацию о себе', callback_data = 'edit_info'))
    markup.add(
        types.InlineKeyboardButton('Просмотр доступных работ', callback_data = 'task'))
    return markup


def setup_student_handlers(bot):
    @bot.callback_query_handler(func = lambda callback: callback.data in ['edit_info'])
    def continue_registration(callback):
        student = get_student(callback.message.chat.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Зарегистрироваться как преподователь или ассистент',
                                              callback_data = 'new_admin'))
        markup.add(types.InlineKeyboardButton('Изменить имя', callback_data = 'update_name'))
        markup.add(types.InlineKeyboardButton('Изменить группу', callback_data = 'update_group'))
        bot.send_message(callback.message.chat.id, f"Ваше имя: {student[2]}.\n"
                                                   f"Ваша группа: {student[1]}.\n"
                                                   f"Выберите, что вы хотите изменить:",
                         reply_markup = markup)

    @bot.callback_query_handler(func = lambda callback: callback.data in ['update_name', 'update_group'])
    def handle_update_request(callback):
        if callback.data == 'update_name':
            bot.send_message(callback.message.chat.id, f"Введите новое имя.")
            bot.register_next_step_handler(callback.message, process_update_name)
        if callback.data == 'update_group':
            bot.send_message(callback.message.chat.id, f"Введите новую группу.")
            bot.register_next_step_handler(callback.message, process_update_group)

    def process_update_name(message):
        new_name = message.text
        update_student_info(message.chat.id, None, new_name)
        student = get_student(message.chat.id)
        bot.send_message(message.chat.id, "Информация изменена.\n"
                                          f"Ваше имя: {student[2]}\n"
                                          f"Ваша группа: {student[1]}",
                         reply_markup = students_keyboard())  # добавить вывод информации

    def process_update_group(message):
        new_group = message.text
        update_student_info(message.chat.id, new_group, None)
        student = get_student(message.chat.id)
        bot.send_message(message.chat.id, "Информация изменена.\n"
                                          f"Ваше имя: {student[2]}\n"
                                          f"Ваша группа: {student[1]}",
                         reply_markup = students_keyboard())
