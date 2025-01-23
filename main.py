from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'ru')
import requests
import telebot
from telebot import types
import re


TOKEN = 'TOKEN'
URL = 'https://api.telegram.org/bot'
CAH = 'Chat Id'
bot = telebot.TeleBot(TOKEN, parse_mode='MARKDOWN')
usersid = ['Users Id']

inputData = {}

   

@bot.message_handler(func=lambda message: message.chat.id not in usersid)
def checkID(message):
   bot.send_message(message.chat.id, "Нет доступа к Боту, обрадитесь к администратору")
   
   
@bot.message_handler(commands=['start', 'stop'])
def handle_start(message: str) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Сообщить')  
    markup.add(item1)
    inputData[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Добро пожаловать!'.format(message.from_user), reply_markup=markup)
    
    
@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Сообщить':
            bot.send_message(message.chat.id, 'Напишите сервис который будет отключен', reply_markup=types.ReplyKeyboardRemove())   
            bot.register_next_step_handler(message, save_service)
         
         #сама отправка   
        elif message.text == 'Отправить':
            current_date = datetime.today().strftime('%d %B %Y')
            service = inputData[message.chat.id]['service']
            startTime = datetime.strftime(inputData[message.chat.id]['startTime'], '%d %B %Y %H:%M')
            endTime = datetime.strftime(inputData[message.chat.id]['endTime'], '%d %B %Y %H:%M')
            requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={CAH}&text=  ℹ️   Обновлению сервисов  \n\n Уважаемые коллеги! \n\n C {startTime} по {endTime}, не будут доступны сервисы {service} \n Приносим свои извинения за доставленные неудобства. \n\n {current_date}')  
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Сообщить')  
            markup.add(item1)
            bot.send_message(message.chat.id, "Сообщение отправлено", reply_markup=markup)
         
         #выбор меню изменения   
        elif message.text == 'Изменить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Изменить сервис')  
            item2 = types.KeyboardButton('Изменить время отключения')  
            item3 = types.KeyboardButton('Изменить время включения')
            item4 = types.KeyboardButton('Назад')
            markup.add(item1, item2, item3, item4)
            bot.send_message(message.chat.id, "Меню изменения", reply_markup=markup)
         
         #   Изменить сервис
        elif message.text == 'Изменить сервис':
            bot.send_message(message.chat.id, "Введите измененный сервис", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, changes_service)
         
         #   
        elif message.text == 'Изменить время отключения':
            bot.send_message(message.chat.id, "Введите измененное время \n(Пример 01.01.2024 10:00)", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, changes_start_time)
        
        elif message.text == 'Изменить время включения':
            bot.send_message(message.chat.id, "Введите измененное время \n(Пример 01.01.2024 10:00)", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, changes_end_time)
            
        elif message.text == 'Назад':
            preview(message)
            
        elif message.text == 'Отмена':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Сообщить')  
            markup.add(item1)
            inputData[message.chat.id] = {}
            bot.send_message(message.chat.id, 'Добро пожаловать!'.format(message.from_user), reply_markup=markup)


# сервис 
def save_service(message):
    if message.text == '/stop':
        return 
    else:
        inputData[message.chat.id]['service'] = message.text
        bot.send_message(message.chat.id, f'Отлично, {message.text}')
        bot.send_message(message.chat.id, f'Укажите c когда сервис перстанет быть доступны \n(Пример 01.01.2024 09:00)')
        bot.register_next_step_handler(message, save_start_time) 

        
        
        
#с какого 
def save_start_time(message):
    if message.text == '/stop':
        return 
    else:
        if re.match(r"^[0-3]\d\.[0-1]\d\.\d{4}\s[0-2]\d\:[0-5]\d$", message.text):
            try:
                startTimeTime = datetime.strptime(str(message.text), '%d.%m.%Y %H:%M')
            except ValueError:
                bot.send_message(message.chat.id, f'{message.text} не правильное значение')
                bot.register_next_step_handler(message, save_start_time)
            else:
                startTimeStr = datetime.strftime(startTimeTime, '%d %B %Y %H:%M')
                inputData[message.chat.id]['startTime'] = startTimeTime
                bot.send_message(message.chat.id, f'Отлично, {startTimeStr}')
                bot.send_message(message.chat.id, f'Укажите дату и время когда будет восстановлен доступ к сервису \n(Пример 01.01.2024 09:30)')
                bot.register_next_step_handler(message, save_end_time)
        else:
            bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
            bot.register_next_step_handler(message, save_start_time)

#по какого числа        
def save_end_time(message):
    if message.text == '/stop':
        return 
    else:
        if re.match(r"^[0-3]\d\.[0-1]\d\.\d{4}\s[0-2]\d\:[0-5]\d$", message.text):
            try:
                endTimeTime = datetime.strptime(str(message.text), '%d.%m.%Y %H:%M')
            except ValueError:
                bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
                bot.register_next_step_handler(message, save_end_time)
            else:
                startTime = inputData[message.chat.id]['startTime']
                if startTime < endTimeTime:
                    endTimeStr = datetime.strftime(endTimeTime, '%d %B %Y %H:%M')
                    inputData[message.chat.id]['endTime'] = endTimeTime
                    bot.send_message(message.chat.id, f'Отлично, {endTimeStr}')
                    preview(message)
                else:
                    bot.send_message(message.chat.id, f'Время восстановления должно быть раньше чем время без доступа, повторите попытку с начала \nУкажите дату и время когда сервис будет не доступент (Пример 01.01.2024 10:00)')
                    bot.register_next_step_handler(message, save_end_time)
        else:
            bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
            bot.register_next_step_handler(message, save_end_time)


 #изменения сервиса     
def changes_service (message):
    if message.text == '/stop':
        return 
    else:
        serviceOld = inputData[message.chat.id]['service']
        inputData[message.chat.id]['service'] = message.text
        bot.send_message(message.chat.id, f'Сервис, изменен с {serviceOld} на {message.text}')
        preview(message)

 
 #изменения со времени   
def changes_start_time(message):
    if message.text == '/stop':
        return 
    else:
        if re.match(r"^[0-3]\d\.[0-1]\d\.\d{4}\s[0-2]\d\:[0-5]\d$", message.text):
            try:
                startTimeTime = datetime.strptime(str(message.text), '%d.%m.%Y %H:%M')
            except ValueError:
                bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
                bot.register_next_step_handler(message, changes_start_time)
            else:
                endTime = inputData[message.chat.id]['endTime']
                if startTimeTime < endTime:
                    startTimeStr = datetime.strftime(startTimeTime, '%d %B %Y %H:%M')
                    startTimeStrOld = datetime.strftime(inputData[message.chat.id]['startTime'], '%d.%m.%Y %H:%M')
                    inputData[message.chat.id]['startTime'] = startTimeTime
                    bot.send_message(message.chat.id, f'Время изменено с {startTimeStrOld} на {startTimeStr}')
                    preview(message)
                else:
                    bot.send_message(message.chat.id, f'Время восстановления должно быть раньше чем время без доступа, повторите попытку с начала \nУкажите дату и время когда сервис будет не доступент (Пример 01.01.2024 10:00)')
                    bot.register_next_step_handler(message, changes_start_time)
        else:
            bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
            bot.register_next_step_handler(message, changes_start_time)
    
 #изменения по времени      
def changes_end_time(message):
    if message.text == '/stop':
        return 
    else:
        if re.match(r"^[0-3]\d\.[0-1]\d\.\d{4}\s[0-2]\d\:[0-5]\d$", message.text):
            try:
                endTimeTime = datetime.strptime(str(message.text), '%d.%m.%Y %H:%M')
            except ValueError:
                bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
                bot.register_next_step_handler(message, changes_end_time)
            else:
                startTime = inputData[message.chat.id]['startTime']
                if endTimeTime > startTime:
                    endTimeStrNew = datetime.strftime(endTimeTime, '%d %B %Y %H:%M')
                    endTimeStrOld = datetime.strftime(inputData[message.chat.id]['endTime'], '%d.%m.%Y %H:%M')
                    inputData[message.chat.id]['endTime'] = endTimeTime
                    bot.send_message(message.chat.id, f'Время изменено с {endTimeStrOld} на {endTimeStrNew}')
                    preview(message)
                else:
                    bot.send_message(message.chat.id, f'Время восстановления должно быть раньше чем время без доступа, повторите попытку с начала \nУкажите дату и время когда сервис будет не доступент (Пример 01.01.2024 10:00)')
                    bot.register_next_step_handler(message, changes_end_time)
        else:
            bot.send_message(message.chat.id, f'{message.text} Не правильное значение')
            bot.register_next_step_handler(message, changes_end_time)
 
 #отправка      
def preview(message):
    current_date = datetime.today().strftime('%d %B %Y')
    service = inputData[message.chat.id]['service']
    startTime = datetime.strftime(inputData[message.chat.id]['startTime'], '%d %B %Y %H:%M')
    endTime = datetime.strftime(inputData[message.chat.id]['endTime'], '%d %B %Y %H:%M')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Отправить')  
    item2 = types.KeyboardButton('Изменить') 
    back = types.KeyboardButton('Отмена') 
    markup.add(item1, item2, back)
    bot.send_message(message.chat.id, f'ℹ️   <b>Обновлению сервисов</b> \n\n Уважаемые коллеги! \n\n C {startTime} по {endTime}, не будут доступны сервисы {service} \n Приносим свои извинения за доставленные неудобства. \n\n {current_date}', reply_markup=markup,  parse_mode='HTML')

while True:
    try:
        bot.polling(none_stop=True)
    except:
        continue