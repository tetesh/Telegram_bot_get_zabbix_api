from pyzabbix import ZabbixAPI
import time

# Проверка подключения
# answer = z.do_request('apiinfo.version')
# print("Version:",answer['result'])

def time_unix(): #Функция получение настроящего времени - 122 секунды в формате unix (Нас интересует только актуальные значения)
    time_unic = int(time.mktime(time.localtime())) - 122
    return time_unic

#time_unix = int(time.mktime(time.localtime())) - 122 #Настроящее время - 122 секунды
#print(time_unix)
#time_unix_3m = int(time_unix) - 122
zabbix_server = "http://192.168.1.100/zabbix"
zabbix_user = "user"
zabbix_password = "password"

z = ZabbixAPI(zabbix_server, user=zabbix_user, password=zabbix_password)
def return_last_history(itemids, history):
    try:
        get = z.history.get(itemids=itemids, sortfield='clock', limit=1, sortorder='DESC', time_from=time_unix(), history=history)
        print(get)
        get_value = get[0]['value']
        return get_value
    except IndexError:
        print('no data')

#информация по запросам zabbix api:       
#https://www.zabbix.com/documentation/current/ru/manual/api/reference/history/get        
        
#примеры:        
#return_temp_1 = round(float(return_last_history(30671, 0)),2)
#return_temp_2 = round(float(return_last_history(30654, 0)),2)

# history=
# History object types to return.
# Possible values:
# 0 - numeric float;
# 1 - character;
# 2 - log;
# 3 - numeric unsigned;
# 4 - text

#   itemids можно получить в веб морде Zabbix, к примеру навести курсор на "график" в меню "последние данные" нужного хоста, посмотрев ссылку
#   так же получать itemids можно в автоматическом режиме через функцию и zabbix.api по запросу из telegram 
#   https://www.zabbix.com/documentation/current/ru/manual/api/reference/host/get

#Получить список групп:
# groups = z.hostgroup.get(output=['itemid','name'])
# for group in groups:
#         print group['groupid'],group['name']

#Получить список хостов в заданной группе (groupids)
# hosts = z.host.get(groupids=4, output=['hostid','name'])
# for host in hosts:
#     print(host['hostid'],host['name'])

#Получить список items выбранного хоста (hostids)
# items = z.item.get(hostids=10084, output=['itemid','name'])
# for item in items:
#     print(item['itemid'],item['name'])
