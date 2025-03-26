import telebot
from telebot import types
import os
from databases_methods.admins_methods import get_all_admin, delete_admin_by_username
from databases_methods.list_of_students_methods import add_by_excel
from databases_methods.key_for_admin import add_key

bot = telebot.TeleBot('7903231812:AAE0zim_gbjgysiiXmHmRsG_P0s33PlxkZs')


# клавиатурка
def main_admin_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Изменить список студентов', callback_data = 'edit_list_of_students'))
    markup.add(types.InlineKeyboardButton('Просмотр администраторов', callback_data = 'list_of_admin'))
    markup.add(
        types.InlineKeyboardButton('Создать новое задание', callback_data = 'create_task'))
    markup.add(
        types.InlineKeyboardButton('Просмотр заданий', callback_data = 'list_of_task'))
    return markup


def setup_main_admin_handlers(bot):
    # просмотр администраторов
    @bot.callback_query_handler(func = lambda callback: callback.data in ['list_of_admin'])
    def get_list_of_admin(callback):
        admins = get_all_admin()
        if not admins:
            bot.send_message(callback.message.chat.id, f"Список администраторов пуст.",
                             reply_markup = main_admin_keyboard())
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Добавить новых администраторов', callback_data = 'add_new_admin'))
            markup.add(types.InlineKeyboardButton('Удалить администратора', callback_data = 'delete_admin'))
            bot.send_message(callback.message.chat.id, f"Список администраторов: \n"
                                                       f"{admins}"
                                                       f"Выберите следующее действие:", reply_markup = markup)

    @bot.callback_query_handler(func = lambda callback: callback.data in ['add_new_admin', 'delete_admin'])
    def change_admins(callback):
        if callback.data == 'add_new_admin':
            bot.send_message(callback.message.chat.id,
                             f"Чтобы добавить новых администраторов, вам нужно создать пароль, который будет действовать 48ч. "
                             f"Выдайте этот пароль людям, которые должны зарегистрироваться, как администраторы. \n"
                             f"Введите пароль:")
            bot.register_next_step_handler(callback.message, process_create_password)
        else:
            bot.send_message(callback.message.chat.id,
                             f"Введите телеграм ник администратора, которого хотите удалить. "
                             f"Если хотите удалить несколько администраторов, введите их ники через пробел.\n"
                             f"Например: abc asd rht")
            bot.register_next_step_handler(callback.message, process_delete_admin)

    def process_create_password(message):
        password = message.text
        tg_id = message.from_user.id
        add_key(tg_id, password)
        bot.send_message(message.chat.id, f"Пароль сохранен!")

    def process_delete_admin(message):
        tg_nik = message.text
        check = delete_admin_by_username(tg_nik)
        new_list = get_all_admin()
        if check:
            bot.send_message(message.chat.id,
                             f"Пользователи успешно удалены из администраторов. Новый список администраторов:\n"
                             f"{new_list}", reply_markup = main_admin_keyboard())
        else:
            bot.send_message(message.chat.id,
                             f"Не удалось удалить кого-то из пользователей из администраторов. Список на данный момент: \n"
                             f"{new_list}", reply_markup = main_admin_keyboard())

    @bot.callback_query_handler(func = lambda callback: callback.data in ['edit_list_of_students'])
    def change_list_of_students(callback):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Создать новый список', callback_data = 'new_list_of_students'))
        markup.add(types.InlineKeyboardButton('Редактировать список', callback_data = 'change_list_of_student'))
        bot.send_message(callback.message.chat.id, f"Выберите следующее действие: ", reply_markup = markup)

    @bot.callback_query_handler(func = lambda callback: callback.data in ['new_list_of_students'])
    def new_list_of_students(callback):
        bot.send_message(callback.message.chat.id,
                         "Пришлите файл со списком студентов в формате, сделанный по следующим правилам:\n"
                         "1) Формат файла: .xlsx или .xls \n"
                         '2) Таблица должна содержать два столбца: имена студентов (этот столбец должен иметь название "full_name"), номер группы (столбец должен называться "group_number")')

    @bot.message_handler(content_types = ['document'])
    def handle_document(message):
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Загружаем файл
        downloaded_file = bot.download_file(file_path)
        local_filename = f"temp_{message.document.file_name}"

        with open(local_filename, "wb") as new_file:
            new_file.write(downloaded_file)

        if not (new_file.endswith('.xlsx') or new_file.endswith('.xls')):
            bot.send_message(message.chat.id, "Ошибка! Отправьте файл в формате Excel (.xlsx или .xls).")
            os.remove(local_filename)
            return

        # Обрабатываем файл
        response = add_by_excel(local_filename)

        # Удаляем временный файл
        os.remove(local_filename)

        # Отправляем ответ пользователю
        bot.send_message(message.chat.id, response)

    @bot.callback_query_handler(func = lambda callback: callback.data in ['create_task'])
    def create_task(callback):
        pass

    @bot.callback_query_handler(func = lambda callback: callback.data in ['list_of_task'])
    def get_list_of_task(callback):
        pass

    # @bot.callback_query_handler(func = lambda callback: callback.data in ['update_name', 'update_group'])
    # def handle_update_request(callback):
    #     if callback.data == 'update_admin_name':
    #         bot.send_message(callback.message.chat.id, f"Введите новое имя.")
    #         bot.register_next_step_handler(callback.message, process_update_name)
    #     if callback.data == 'update_admin_group':
    #         bot.send_message(callback.message.chat.id, f"Введите новый список групп.")
    #         bot.register_next_step_handler(callback.message, process_update_group)
