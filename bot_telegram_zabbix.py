import telebot, requests, os, psutil, zabbix_api

#API токен получаем в BotFather
bot = telebot.TeleBot("ADD TOKEN")

#Учетные данные от API Zabbix и разрешенные ID пользователей и группы для запросов
zabbix_server = "http://192.168.1.100/zabbix" 
zabbix_user = "user"
zabbix_password = "password"
id_allow = ['xxxxxxxxxx', 'xxxxxxxxxx']

#Переключение на модем в случае недоступности Wi-fi (Должны быть установлены статические адреса)
#if os.system("ping -c 2 192.168.1.100") == 0:
#    zabbix_server = "http://192.168.1.100/zabbix"
#    print(f'\nВыбран Zabbix server: {zabbix_server}')
#else:
#    zabbix_server = "http://192.168.8.100/zabbix"
#    print(f'\nВыбран Zabbix server: {zabbix_server}')
    
#постоянные ссылки на графики полученные из веб морды Zabbix (graphid получаем в настройках хоста в предпросмотре графика, график должен быть создан взаранее!)
temp_return = zabbix_server + '/chart2.php?fullscreen=0&graphid=1214&width=1138&period=43300'
temp_supply = zabbix_server + '/chart2.php?fullscreen=0&graphid=1213&width=1138&period=43300'
humidity_return = zabbix_server + '/chart2.php?fullscreen=0&graphid=1228&width=1138&period=43300'
fans = zabbix_server + '/chart2.php?fullscreen=0&graphid=1229&width=1138&period=43300'
v_input = zabbix_server + '/chart2.php?fullscreen=0&graphid=1217&width=1138&period=43300'
ups_time = zabbix_server + '/chart2.php?fullscreen=0&graphid=1230&width=1138&period=43300'

def get_zabbix_img(graph_url):
    try:
        data_api = {"name": zabbix_user, "password": zabbix_password, "enter": "Sign in"}
        req_cookie = requests.post(zabbix_server + "/", data=data_api)
        cookie = req_cookie.cookies
        res = requests.get(graph_url, cookies=cookie)
        b = open('graph.png', 'wb')
        b.write(res.content) # Сохраняем график в файл graph.png
        b.close()
        return b  # Возвращает PNG с нужным графиком (в данном скрипте не важно)
    except BaseException:
        print('Произошла ошибка, при получении графика')

#Приветствие
@bot.message_handler(commands=['help', 'start']) #обрабатываем только указанные комманды
def welcome(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
    keyboard.row('/start', '/temp_return', '/temp_supply') #Создаем кнопки
    keyboard.row('/humidity', '/fans', '/ups_time') #Создаем кнопки
    keyboard.row('/v_input', '/battery_notebook', '/get_all')
    bot.send_message(message.chat.id, '''Привет, я бот! #Отправляем сообщение и созданные кнопки
Список доступных команд:
/start - Инициализация (с получением кнопок telegram)
/temp_return - Температура горячего корридора
/temp_supply - Температура холодного корридора
/humidity - Влажность
/fans - Вентиляторы
/ups_time - Предполагаемое оставшее время работы от АКБ (В случае отключения всех источников питания)
/v_input - Напряжение на входе UPS
/battery_notebook - Получение информации о заряде ноутбука
/get_all - Сводная информация по кондиционерам и UPS
''', reply_markup=keyboard) 

@bot.message_handler(content_types=["text"]) #слушаем весь текст и обрабатываем, что нам нужно
def text_processing(message):
    if str(message.from_user.id) in id_allow: #проверяем есть ли ID в разрешенных
        if message.text.lower() == '/temp_return' or message.text.lower() == '/temperature_return': # сообщения которые будут обрабатываться
            get_zabbix_img(temp_return) # Вызов функции с нужной ссылкой
            bot.send_photo(message.chat.id, photo=open('graph.png', 'rb'), reply_to_message_id=message.message_id)

        elif message.text.lower() == '/temp_supply' or message.text.lower() == '/temperature_supply': 
            get_zabbix_img(temp_supply)
            bot.send_photo(message.chat.id, photo=open('graph.png', 'rb'), reply_to_message_id=message.message_id)

        elif message.text.lower() == '/humidity' or message.text.lower() == '/humidity_return': 
            get_zabbix_img(humidity_return)
            bot.send_photo(message.chat.id, photo=open('graph.png', 'rb'), reply_to_message_id=message.message_id)

        elif message.text.lower() == '/fans' or message.text.lower() == '/fans_all': 
            get_zabbix_img(fans)
            bot.send_photo(message.chat.id, photo=open('graph.png', 'rb'), reply_to_message_id=message.message_id)

        elif message.text.lower() == '/v_input' or message.text.lower() == '/input_v': 
            get_zabbix_img(v_input)
            bot.send_photo(message.chat.id, photo=open('graph.png', 'rb'), reply_to_message_id=message.message_id)

        elif message.text.lower() == '/ups_time' or message.text.lower() == '/time_ups': 
            get_zabbix_img(ups_time)
            bot.send_photo(message.chat.id, photo=open('graph.png', 'rb'), reply_to_message_id=message.message_id)

#        elif message.text.lower() == '/battery_notebook' or message.text.lower() == '/battery': #В поем случае zabbix на ноутбуке, я получаю % заряда черезе psutil, если нужно раскомментируйте
#            bot.send_message(message.chat.id, f'Питание присутсвует? - {psutil.sensors_battery().power_plugged}\nЗаряд батареи ноутбука - {round(psutil.sensors_battery().percent, 1)}')

        elif message.text.lower() == '/get_all': #Общая информация текстом, через Zabbix_api модуль
            try:
                bot.send_message(message.chat.id, 
f'''
!                              t return     t supply
Кондиционер 1      {round(float(zabbix_api.return_last_history(30671, 0)),2)}          {round(float(zabbix_api.return_last_history(30674, 0)),2)}
Кондиционер 2      {round(float(zabbix_api.return_last_history(30654, 0)),2)}          
Кондиционер 3      {round(float(zabbix_api.return_last_history(30688, 0)),2)}          {round(float(zabbix_api.return_last_history(30691, 0)),2)}
Кондиционер 4      {round(float(zabbix_api.return_last_history(30705, 0)),2)}          {round(float(zabbix_api.return_last_history(30708, 0)),2)}
Кондиционер 5      {round(float(zabbix_api.return_last_history(30722, 0)),2)}          {round(float(zabbix_api.return_last_history(30725, 0)),2)}
                   Input v1: {round(float(zabbix_api.return_last_history(30873, 3)),2)}v
UPS           Input v2: {round(float(zabbix_api.return_last_history(30886, 3)),2)}v
                   Input v3: {round(float(zabbix_api.return_last_history(30884, 3)),2)}v
'''
)
            except TypeError: #Если zabbix api вернул пустое значение(Мы запрашиваем последнее значение, поступившее за последние 3 минуты), появляется исключение TypeError
                bot.send_message(message.chat.id, 'В базе данных отсутствуют данные в течение более двух минут!')   
    else:
        bot.send_message(message.chat.id, "Вам не разрешено это запрашивать! ")



bot.polling(none_stop=True, interval=0) # Бот слушает сообщения постоянно
