import logging
from telebot import types
from databases_methods.students_methods import update_student_info, get_student_by_tg_id

logging.basicConfig(
    filename = "bot_errors.log",
    level = logging.ERROR,
    format = "%(asctime)s - %(levelname)s - %(message)s",
)


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
        try:
            student = get_student_by_tg_id(callback.message.chat.id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Зарегистрироваться как преподователь или ассистент',
                                                  callback_data = 'new_admin'))
            markup.add(types.InlineKeyboardButton('Изменить имя', callback_data = 'update_name'))
            markup.add(types.InlineKeyboardButton('Изменить группу', callback_data = 'update_group'))
            bot.send_message(callback.message.chat.id, f"Ваше имя: {student[2]}.\n"
                                                       f"Ваша группа: {student[1]}.\n"
                                                       f"Выберите, что вы хотите изменить:",
                             reply_markup = markup)
        except Exception as e:
            logging.error(f"Ошибка в continue_registration: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['update_name', 'update_group'])
    def handle_update_request(callback):
        try:
            if callback.data == 'update_name':
                bot.send_message(callback.message.chat.id, f"Введите новое имя")
                bot.register_next_step_handler(callback.message, process_update_name)
            if callback.data == 'update_group':
                bot.send_message(callback.message.chat.id, f"Введите новую группу")
                bot.register_next_step_handler(callback.message, process_update_group)
        except Exception as e:
            logging.error(f"Ошибка в handle_update_request: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    def process_update_name(message):
        try:
            new_name = message.text
            check = update_student_info(message.from_user.id, None, new_name)
            student = get_student_by_tg_id(message.from_user.id)
            if check[0] == False:
                bot.send_message(message.chat.id, "Не удалось обновить информацию", reply_markup = students_keyboard())
            elif check[0] == True and check[1] == True:
                bot.send_message(message.chat.id, "Информация изменена, вы найдены в списке лектора!\n"
                                                  f"Ваше имя: {student[2]}\n"
                                                  f"Ваша группа: {student[1]}",
                                 reply_markup = students_keyboard())
            elif check[0] == True and check[1] == False:
                bot.send_message(message.chat.id, "Информация изменена, но вы не найдены в списке лектора.\n"
                                                  f"Ваше имя: {student[2]}\n"
                                                  f"Ваша группа: {student[1]}",
                                 reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_update_name: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")


    def process_update_group(message):
        try:
            new_group = message.text
            check = update_student_info(message.from_user.id, new_group, None)
            student = get_student_by_tg_id(message.from_user.id)
            if check[0] == False:
                bot.send_message(message.chat.id, "Не удалось обновить информацию", reply_markup = students_keyboard())
            elif check[0] == True and check[1] == True:
                bot.send_message(message.chat.id, "Информация изменена, вы найдены в списке лектора!\n"
                                                  f"Ваше имя: {student[2]}\n"
                                                  f"Ваша группа: {student[1]}",
                                 reply_markup = students_keyboard())
            elif check[0] == True and check[1] == False:
                bot.send_message(message.chat.id, "Информация изменена, но вы не найдены в списке лектора.\n"
                                                  f"Ваше имя: {student[2]}\n"
                                                  f"Ваша группа: {student[1]}",
                                 reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_update_group: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")
