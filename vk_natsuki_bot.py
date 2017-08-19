import time
import vk_api
import random
import requests
import os
from bs4 import BeautifulSoup
#Создание экземпляра класса, для работы с api VK
vk = vk_api.VkApi(login='+79231412276', password='', token='d4f357670aff1adc1fb0cfb05b314f3336d89b6dce2fc8f37a0b47208d54395f5e3d46fb2697b6c5431fc')
#Аунтетификация
vk.auth()
#Метод, который будет выполнять поисковой запрос на сайте и возращать полученные данные в виде списка
def find_anime(body):
    try:
        #Основной адрес
        URL = "http://animeonline.su"
        #Адрес для поиска
        search_url = "http://animeonline.su/search/"
        #Получаем нужные данные
        body.replace('"', '')
        l = body.split()
        l.remove("Нацуки,")
        l.remove("аниме")
     
        s=""
        i=0
        for word in l:
            i+=1
            s+=word
            if i<len(l):
                s+="_"
        #Формируем поисковой запрос
        search_url+=s
        #Получаем код нужной страницы
        doc = requests.get(search_url)
        #Трансформируем его в экземпляр класса BeatifulSoup, с помощью которого и будет происходить парсинг
        soup = BeautifulSoup(doc.text, "lxml")
        #Получаем ссылку на нужную страницу
        anime_url = soup.find("div", {'class' : "poster_container"}).find("a").get("href")
        doc_a = requests.get(anime_url)
        soup_a = BeautifulSoup(doc_a.text, "lxml")
        #Получаем данные из первого попавшегося варианта в поиске
        img = URL + soup_a.find("div", {'class' : 'poster_container'}).find("img").get("src")
        
        name_rus = str(soup_a.find("h1", {"class" : "nameMain"})).replace('<h1 class="nameMain" itemprop="name">','').replace("</h1>", "")
        name_of = str(soup_a.find("h2", {"class" : "nameAlt"})).replace('<h2 class="nameAlt" itemprop="alternativeHeadline">','').replace("</h2>", "")
        
        descr = requests.get(anime_url)
        descr_html = descr.text
        
        soup_descr = BeautifulSoup(descr_html, "lxml")
        description = soup_descr.find("meta", {"name":"description"}).get("content")
        if description == " " or description=="":
            description = "Отсутсвует."
        final_text = "Название : "+name_rus+" ("+name_of+")"+'\n'+'Описание : '+description
        #Упаковываем всё в список и возращаем
        return {"image_url" : img, "text" : final_text}
    except:
        return None
#Метод для отправки сообщения пользователю VK
def write_msg(user_id, s):
    vk.method('messages.send', {'user_id':user_id,'message':s})
#Метод для отправки сообщения с медиафайлами
def send_attahc(user_id, at, s=None):
    if s == None:
        vk.method('messages.send', {'user_id':user_id,'attachment':at})
    else:
        vk.method('messages.send', {'user_id':user_id,'attachment':at, 'message':s})
#Сохранение картинки во временный файл
def download_photo_and_save_in_tempfile(photo_url):
    img_resp = requests.get(photo_url)
    img_name = 'lel.png'
    img_file = open(img_name, 'wb')
    img_file.write(img_resp.content)
    img_file.close()
    return img_name
#Загрузка картинки на сервера VK
def upload_photo(photo):
    url = vk.method('photos.getMessagesUploadServer')
    file_ph = {'photo': open(photo, 'rb')}
    upload_resp = requests.post(url['upload_url'], files = file_ph)
    data = upload_resp.json()
    response = vk.method('photos.saveMessagesPhoto', {'server':data['server'],'photo':data['photo'], 'hash':data['hash']})
    print(response)
    return response[0]['id']
#Отправка картинки
def send_photo_to_user(user_id, photo_name, mess=None):
    id_p = upload_photo(photo_name)
    owner = "341518179"
    attach_inf = 'photo{0}_{1}'.format(owner, id_p)
    if mess==None:
        send_attahc(user_id, attach_inf)
    else:
        send_attahc(user_id, attach_inf, mess)
#Взаимодействие бота и пользователя
def mogvai(user_id,body=None):
    if body.lower().startswith("нацуки привет") or body.lower().startswith("нацуки, привет"):
        write_msg(user_id, "Команда подтверждена.\n Открываю пятые врата.\n -Здравствуй, друг.")
    if body.lower().startswith("нацуки проверь") or body.lower().startswith("нацуки, проверь"):
        write_msg(user_id, "Вероятность этого - {0}%, я полагаю.".format(random.randint(0, 100)))
    elif body.lower().startswith("нацуки, аниме"):
        anime_info = find_anime(body)
        if anime_info!=None:
            name = download_photo_and_save_in_tempfile(anime_info['image_url'])
            send_photo_to_user(user_id, name, anime_info['text'])
        else:
            write_msg(user_id, "Прошу прощения. Аниме не было найдено.")
    else:
        return None
getmsg_values = {'out':0, 'count':10, 'time_offset':1}
print("*****STARTED*****")
#Бесконечный цикл прослушки входящих сообщений
while True:
    msg = vk.method('messages.get', getmsg_values)
    for item in msg['items']:
        print("#############NEW ITEM###############")
        print(item)
        mogvai(item['user_id'], item['body'])
    time.sleep(1)