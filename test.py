import telebot
import os
import requests
import time
import config
from bs4 import BeautifulSoup as bs
import pyexcel as pe
import re
import pandas as pd

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Отправь ссылку на фид для конвертации в таблицу")
        
@bot.message_handler(content_types=["text"]) 
def first(message):
    #HEADERS = {
    #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 YaBrowser/21.2.0.1122 Yowser/2.5 Safari/537.36'
    #}
    bot.send_message(message.chat.id, "Создаю таблицу")
    response = requests.get(message.text)#, headers=HEADERS)
    soup = bs(response.content, 'xml')
    offer = soup.find_all('offer')

    offers = []
    offers2 = []
    categorys = ['часть дома','квартира','flat','таунхаус', 'townhouse','дуплекс','duplex','дача', 'коттедж','cottage','дом', 'house']

    for item in offer:
        errors = []
        newbuilding_tags = []
        newbuilding_errors = []
        offer = item.get('internal-id')
            

        type_offer = item.find('type')
        if type_offer:
            type_offer = type_offer.get_text()
        if type_offer is None:
            type_offer = ' - '

        commercial_type = item.find('commercial-type')
        if commercial_type:
            commercial_type = commercial_type.get_text()
        if commercial_type is None:
            commercial_type = ' - '

        commercial_building_type = item.find('commercial-building-type')
        if commercial_building_type:
            commercial_building_type = commercial_building_type.get_text()
        if commercial_building_type is None:
            commercial_building_type = ' - '


        purpose = item.find('purpose')
        if purpose:
            purpose = purpose.get_text()
        if purpose is None:
            purpose = ' - '

        prop_type = item.find('property-type')
        if prop_type:
            prop_type = prop_type.get_text()
        if prop_type is None:
            prop_type = ' - '

        category = item.find('category')
        if category:
            category = category.get_text()
        if category is None:
            category = ' - '

        price = item.find('price')
        if price:
            price = price.get_text()
        price = re.sub(r'[RUB]', '', price)
        if price is None:
            price = 'ошибка: не указана стоимость объекта'
            errors.append(price)

        area = item.find('area')
        if area:
            area = area.get_text()
            area = re.sub(r'[\s ]', '', area)
            area = re.sub('кв.м', '', area)
            area = re.sub('sq.m', '', area)

        if area is None:
            area = ' - '


        images = item.find_all('image')
        count_images = len(images)


        floor = item.find('floor')
        if floor:
            floor = floor.get_text()
        if floor is None:
            floor = ' - '

        floors_total = item.find('floors-total')
        if floors_total:
            floors_total = floors_total.get_text()
        if floors_total is None:
            floors_total = ' - '

        country = item.find('country')
        if country:
            country = country.get_text()
        if country is None:
            country = ' - '

        region = item.find('region')
        if region:
            region = region.get_text()
        if region is None:
            region = ' - '

        district = item.find('district')
        if district:
            district = district.get_text()
        if district is None:
            district = ' - '
            
        locality_name = item.find('locality-name')
        if locality_name:
            locality_name = locality_name.get_text()
        if locality_name is None:
            locality_name = ' - '

        sublocality_name = item.find('sub-locality-name')
        if sublocality_name:
            sublocality_name = sublocality_name.get_text()
        if sublocality_name is None:
            sublocality_name = ' - '

        address = item.find('address')
        if address:
            address = address.get_text()
        if address is None:
            address = ' - '

        rooms = item.find('rooms')
        if rooms:
            rooms = rooms.get_text()
        if rooms is None:
            rooms = ' - '
        
        rooms_offered = item.find('rooms-offered')
        if rooms_offered:
            rooms_offered = rooms_offered.get_text()
        if rooms_offered is None:
            rooms_offered = ' - '

        living_space = item.find('living-space')
        if living_space:
            living_space = living_space.get_text()
            living_space = re.sub(r'[\s ]', '', living_space)
            living_space = re.sub('кв.м', '', living_space)
            living_space = re.sub('sq.m', '', living_space)

        if living_space is None and category in categorys:
            living_space = ' - '
        if area == living_space and category in categorys:
            living_space = 'ошибка: общая и жилая площадь не могут быть равны'
            errors.append(living_space)
            
        if living_space is None:
            living_space = ' - '
        
        if living_space is None and type_offer == 'аренда':
            living_space = 'ошибка: в разделе аренды жилья обязательно указывать жилую площадь'
        
        if living_space == '0' and category in categorys:
            living_space = 'ошибка: жилая площадь не может быть равна 0'
            errors.append(living_space)

        year = item.find('built-year')
        if year:
            year = year.get_text()
            if year in ['2020','2021', '2022', '2023', '2024', '2025', '2026'] and category in ['flat', 'квартира'] and type_offer == 'продажа':
                newbuilding_tags.append(year)        
        if year is None:
            year = ' - '   

        building_name = item.find('building-name')
        if building_name:
            building_name = building_name.get_text()
        if building_name is None:
            building_name = ' - '
            
        building_id = item.find('yandex-building-id')
        if building_id:
            building_id = building_id.get_text()
        if building_id is None and year in newbuilding_tags:
            building_id = 'ошибка: не заполнен yandex-building-id'
            errors.append(building_id)
            newbuilding_errors.append(building_id)
        if building_id is None:
            building_id = ' - '

        house_id = item.find('yandex-house-id')
        if house_id:
            house_id = house_id.get_text()
        if house_id is None and year in newbuilding_tags:
            house_id = 'ошибка: не заполнен yandex-house-id'
            errors.append(house_id)
            newbuilding_errors.append(house_id)
        if house_id is None:
            house_id = ' - '

        ready_quarter = item.find('ready-quarter')
        if ready_quarter:
            ready_quarter = ready_quarter.get_text()
        if ready_quarter is None:
            ready_quarter = ' - '  

        new_flat = item.find('new-flat')
        if new_flat:
            new_flat = new_flat.get_text()
        if new_flat is None:
            new_flat = ' - '

        deal_status = item.find('deal-status')
        if deal_status:
            deal_status = deal_status.get_text()
        if deal_status is None:
            deal_status = ' - '

        studio = item.find('studio')
        if studio:
            studio = studio.get_text()
        if studio is None:
            studio = ' - '

        lot_area = item.find('lot-area')
        if lot_area:
            lot_area = lot_area.get_text()
        if lot_area is None:
            lot_area = ' - '

        buildstate = item.find('building-state')
        if buildstate:
            buildstate = buildstate.get_text()
        if buildstate is None and year in newbuilding_tags:
            buildstate = 'ошибка: не заполнен building-state'
            errors.append(buildstate)
            newbuilding_errors.append(buildstate)
        if buildstate is None:
            buildstate = ' - '

        latitude = item.find('latitude')
        if latitude:
            latitude = latitude.get_text()
        if latitude is None:
            latitude = ' - '

        longitude = item.find('longitude')
        if longitude:
            longitude = longitude.get_text()
        if longitude is None:
            longitude = ' - '

        phone = item.find('phone')
        if phone:
            phone = phone.get_text()
        if phone is None:
            phone = ' - '

        salesname = item.find('name')
        if salesname:
            salesname = salesname.get_text()
        if salesname is None:
            salesname = ' - '

        offers.append({
            'price':price.strip(),
            'square\narea':area.strip(),
            'square\nlot-area':lot_area.strip(),
            'Внутренний ID':offer.strip(), 
            'floor':floor.strip(),
            'floors-total':floors_total.strip(),
            'location1\ncountry':country.strip(),
            'location4\nlocality-name':locality_name.strip(),
            'location6\naddress':address.strip(),
            'rooms':rooms.strip(),
            'square\nliving-space':living_space,
            '1 type':type_offer.strip(),
            '2 property-type':prop_type.strip(),
            '3 category':category.strip(),
            'newbuildings\nyandex-building-id':building_id.strip(),
            'newbuildings\nyandex-house-id':house_id.strip(),
            'newbuildings\nnew-flat':new_flat.strip(),
            '4 deal-status':deal_status.strip(),
            '5 commercial-type':commercial_type.strip(),
            '6 purpose':purpose.strip(),
            '7 commercial-building-type':commercial_building_type.strip(),
            'newbuildings\nbuilt-year':year.strip(),
            'newbuildings\nready-quarter':ready_quarter.strip(),
            'newbuildings\nbuilding-name':building_name.strip(),
            'newbuildings\nbuilding-state':buildstate,
            'rooms-offered':rooms_offered.strip(),
            'location3\ndistrict':district.strip(),
            'location2\nregion':region.strip(),
            'location5\nsub-locality-name':sublocality_name.strip(),
            'location6\nlatitude':latitude,
            'location7\nlongitude':longitude,
            'studio':studio.strip(),
            'количество\nфотографий':count_images,
            'номер телефона':phone,
            'имя агента':salesname,
            })    

        offers2.append({
            'Внутренний ID':offer.strip(), 
            'type':type_offer.strip(),
            'category':category.strip(),
            'количество\nфотографий':count_images,
            'номер телефона':phone,
            'имя агента':salesname,
            })    

    nametable1 = 'фид' + str(message.chat.id) + '.xlsx'
    pe.save_as(records=offers, dest_file_name=nametable1)
    
    nametable2 = 'без тегов ' + str(message.chat.id) + '.xlsx'
    pe.save_as(records=offers2, dest_file_name=nametable2)

    with open(nametable1, 'rb') as file2send:
        bot.send_document(message.chat.id, file2send)
        file2send.close()
    
    bot.send_message(message.chat.id, "Отправь xls файл с ошибками из личного кабинета, если нужно прикрепить к офферам описание ошибки")
    offers = []
    offfers2 = []

@bot.message_handler(content_types=["document"])
def handle_docs_audio(message):
    try:
        nametable1 = 'фид' + str(message.chat.id) + '.xlsx'
        nametable2 = 'без тегов ' + str(message.chat.id) + '.xlsx'
        save_dir = os.getcwd()
        file_name = message.document.file_name
        file_id = message.document.file_name
        file_id_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_id_info.file_path)
        src = file_name
        with open(save_dir + "/" + src, 'wb') as new_file:
            new_file.write(downloaded)
            new_file.close()
        bot.send_message(message.chat.id, "[*] Файл добавлен\nПрикрепляю ошибки и описание к таблице")
        os.rename(file_name, "report.xls")


        feed = pd.read_excel(nametable1).astype(str)
        feed2 = pd.read_excel(nametable2).astype(str)
        errors = pd.read_excel('report.xls').astype(str)
        descript = pd.read_excel('descr4.xlsx')
        del errors ['Заголовок кластера']

        merged_tables = pd.merge(feed, errors, how='left', on='Внутренний ID')
        with_errors = pd.merge(merged_tables, descript, how='inner', on='Код ошибки')
        
        merged_tables2 = pd.merge(feed2, errors, how='left', on='Внутренний ID')
        with_errors2 = pd.merge(merged_tables2, descript, how='inner', on='Код ошибки')

        filename1 = 'ошибки с тегами ' + str(message.chat.id) + '.xlsx'
        with_errors.to_excel(filename1, index=False)
        filename2 = 'ошибки без тегов ' + str(message.chat.id) + '.xlsx'
        with_errors2.to_excel(filename2, index=False)

        with open(filename1, 'rb') as file_to_send:
            bot.send_document(message.chat.id, file_to_send)
            file_to_send.close()
        with open(filename2, 'rb') as file_to_send:
            bot.send_document(message.chat.id, file_to_send)
            file_to_send.close()

        os.remove("report.xls")
        os.remove(nametable1)
        os.remove(nametable2)
        os.remove(filename1)
        os.remove(filename2)
        bot.send_message(message.chat.id, "Готово, отправь ссылку на фид, если понадобится снова")
    except Exception as ex:
        bot.send_message(message.chat.id, "[!] ошибка - {}".format(str(ex)) + "\nНажмите --> /start и дождитесь ответа от бота")


def telegram_polling():
    try:
        bot.polling(none_stop=True) 
    except Exception as ex:
        with open("Error.txt", "a") as myfile:
            myfile.write("\r\n<<ERROR polling>>\r\n - {}".format(str(ex)))
        time.sleep(10)
        telegram_polling()

if __name__ == '__main__':
    telegram_polling()


