import os
import config
import telebot
import pyAesCrypt
import logging
import requests
from telebot import types

print('Import completed')
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Логииииии
bot = telebot.TeleBot(config.token)  # Токен бота (окремий файл config.py)
task = bot.get_me()
bufferSize = config.bufferSize  # Буфер для шифрування
startkeyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
menucryptkey = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
universalkey = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
helpkeyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton('Зв\'язок з розробником')
itembtn2 = types.KeyboardButton('Проект на Github')
helpkeyboard.add(itembtn1, itembtn2)
startkeyboard.row('Детальніше', 'HELP!!!')
menucryptkey.row('Зашифрувати', 'Розшифрувати')
universalkey.row('Головне меню')
bot_state = "pending"
password = "nothing"
GET_LEN = 7
GET_LEN2 = 9


def set_sate(s):
    global bot_state
    bot_state = s


def get_state():
    return bot_state


def get_password(x):
    global password
    password = x


@bot.message_handler(commands=['start', 'menu'])  # Good mornin'ya
def start_message(message):
    bot.send_message(message.chat.id,
                     'Ну привіт, ' + message.from_user.first_name + '.\nНе хочеш щось зашифрувати?\nЯ можу зашифрувати файл до 20 мб з твоїм паролем.',
                     reply_markup=startkeyboard)


@bot.message_handler(commands=['help'])  # Хелп блять, а то я не витримую блять!
def help_message(message):
    bot.send_message(message.chat.id, 'Що сталося, друже?', reply_markup=helpkeyboard)
    if message.text == 'HELP!!!':
        bot.send_message(message.chat.id, 'Що сталося, друже?', reply_markup=helpkeyboard)
    elif message.text == 'Зв\'язок з розробником':
        bot.send_message(message.chat.id, 'Зв\'язок з @imGlitch.\nВін тобі допоможе розібратися з цим гівном.',
                         reply_markup=helpkeyboard)
    elif message.text == 'Проект на Github':
        bot.send_message(message.chat.id, 'Ще немає на Гітхабі. Соре', reply_markup=universalkey)


@bot.message_handler(commands=['crypt'])  # Шифрувати вмію, диви не потечи
def crypt_file(message):
    passwords = message.text[GET_LEN:]
    print(passwords)
    if passwords == '':
        bot.send_message(message.chat.id, 'Напиши пароль одразу з командою.\nSyntax: /crypt [password]')
        return
    else:
        bot.send_message(message.chat.id, 'Кинь мені файл, який хочеш зашифрувати.\n')
        get_password(passwords)
        print(passwords)
        set_sate("crypt")
        print(bot_state)


@bot.message_handler(commands=['decrypt'])  # А тут я розшифровую, та
def decrypt_file(message):
    passwords = message.text[GET_LEN2:]
    print(passwords)
    if passwords == '':
        bot.send_message(message.chat.id, 'Напиши пароль одразу з командою.\nSyntax: /decrypt [password]')
        return
    else:
        bot.send_message(message.chat.id,
                         'Кинь файл, який хочеш дешифрувати.\nЯ можу розшифрувати файли зі своїм розширенням *.crypt')
        get_password(passwords)
        print(passwords)
        set_sate("decrypt")
        print(bot_state)


@bot.message_handler(content_types=['document'])  # Це кароч тєма яка ловить файл який кидають, да
def handle_file(message):
    print(get_state())
    if get_state() == "crypt":
        try:
            chat_id = message.chat.id
            file_info = bot.get_file(message.document.file_id)
            print(file_info)
            print(bot.get_file(file_info.file_id))
            downloaded_file = bot.download_file(file_info.file_path)
            print(downloaded_file)
            src = message.document.file_name
            with open(src, 'wb+') as new_file:
                new_file.write(downloaded_file)

            file = src

            try:
                pyAesCrypt.encryptFile(str(file), str(file) + ".crypt", password, bufferSize)
            except FileNotFoundError:
                print("File not found!")
            else:
                bot.send_message(message.chat.id, 'Файл зашифрованно!')
                print("File '" + str(file) + ".crypt' successfully saved!")
                file = open(file + '.crypt', 'rb')
                bot.send_document(chat_id, file)
                file.close()
        except Exception as e:
            bot.reply_to(message, e)
    elif get_state() == "decrypt":
        try:
            chat_id = message.chat.id
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = message.document.file_name
            with open(src, 'wb+') as new_file:
                new_file.write(downloaded_file)

            file = src

            try:
                pyAesCrypt.decryptFile(str(file), str(os.path.splitext(file)[0]), password, bufferSize)

            except FileNotFoundError:
                print("File not found!")
            else:
                print("File успішно збережено!")
                file = open(os.path.splitext(file)[0], 'rb')
                bot.send_document(chat_id, file)
                file.close()
        except Exception as e:
            bot.reply_to(message, e)
    else:
        bot.send_message(message.chat.id, 'Не правильно використовуєш, напиши /help')


@bot.message_handler(content_types=['text'])  # А це кароч ІСКУСТВЄНИЙ ІНТЕЛЕКТ (нєт)
def send_text(message):
    if message.text == 'HELP!!!':
        bot.send_message(message.chat.id, 'Що сталося, друже?', reply_markup=helpkeyboard)
    elif message.text == 'Зв\'язок з розробником':
        bot.send_message(message.chat.id, 'Зв\'язок з @imGlitch.\nВін тобі допоможе розібратися з цим гівном.',
                         reply_markup=helpkeyboard)
    elif message.text == 'Проект на Github':
        bot.send_message(message.chat.id, 'Ще немає на Гітхабі. Соре', reply_markup=universalkey)
    elif message.text == 'Детальніше':
        bot.send_message(message.chat.id,
                         'Цей бот може зашифрувати файл та розшифрувати його ж назад за допомогою твого паролю.\n Максимально допустимий розмір 20 МБ\n\nЩо саме ти хочеш зробити?',
                         reply_markup=menucryptkey)
    elif message.text == 'Зашифрувати':
        bot.send_message(message.chat.id, 'Напиши команду /crypt [тут твій придумай пароль для шифрування]')
    elif message.text == 'Розшифрувати':
        bot.send_message(message.chat.id, 'Напиши команду /decrypt [тут твій пароль придуманий до того]')
    elif message.text == 'Головне меню':
        bot.send_message(message.chat.id, 'Прошу', reply_markup=startkeyboard)


bot.polling(none_stop=True)  # Спати то не наше, 24/7/365
