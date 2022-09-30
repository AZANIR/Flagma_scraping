#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
import time
from PIL import ImageOps, Image

from lxml import etree
import requests
from proxy_config import login, password, proxy
from datetime import datetime
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

proxies = {
    'https': f'http://{login}:{password}@{proxy}'
}

cur_date = datetime.now().strftime('%m_%d_%Y')


def get_data(url):
    next_page = True
    page_number = 1

    while next_page:
        print(url + f'page-{page_number}')
        response = session.get(url=url + f'page-{page_number}', headers=headers)
        # print(response.text)

        soup = BeautifulSoup(response.text, 'lxml')
        links_list = []
        with open(file=f'links_{cur_date}.txt', mode='a', encoding='utf-8') as file:
            for link in soup.select('.page-list-item .header a'):
                links_list.append(link.get('href'))
                # print(link.get('href'))
                file.write(link.get('href') + '\n')

        if soup.select("li.next a[onclick^='goToPage']"):
            print("Have next")
        else:
            next_page = False
        time.sleep(1.5)
        page_number = page_number + 1


def parse_advert(url):
    data = []
    response = session.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    # search link
    try:
        search_link = soup.select('.bread-crumbs .search-link')[0].text.strip()
    except:
        search_link = soup.select(".bread-crumbs [itemprop='itemListElement'] a span")[-1-1].text.strip()
    # category
    category = soup.select(".bread-crumbs [itemprop='itemListElement'] a span")[-1].text.strip()
    # title
    title = etree.HTML(str(soup)).xpath('//div[@class="card-m"]//h1')[0].text.strip()
    # description
    description = replace_chars(soup.find('div', id='description').text.strip())
    # contact name
    try:
        contact_name = etree.HTML(str(soup)).xpath('//div[@class="user-name"]')[0].text.strip()
    except:
        contact_name = etree.HTML(str(soup)).xpath('//div[@class="user-name"]/span')[0].text.strip()
    # company info
    company_info = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-info']//span")[
        0].text.strip()
    company_info_2 = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-info']//span")[
        1].text.strip().split(',')[0]
    # count adv
    count_adv = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-ads-link']/a")[
        0].text.strip()
    # photo
    photo_list = save_photo(soup.select('.card-m .small-photos-block img'))
    # phones
    phone_list = get_phones(soup.select('a.tel'))

    data.append(url)
    data.append(search_link)
    data.append(category)
    data.append(title)
    data.append(description)
    data.append(contact_name)
    data.append(company_info)
    data.append(company_info_2)
    data.append(count_adv)
    data.append(photo_list)
    data.append(phone_list)
    print(url)
    print(" ->")
    # print(search_link)
    # print(category)
    # print(title)
    # print(description)
    # print(contact_name)
    # print(company_info)
    # print(company_info_2)
    # print(count_adv)
    # print(photo_list)
    # print(phone_list)
    time.sleep(random.randint(5, 13))  # set timeout if we dont have parse items
    return data


def replace_chars(string_data):
    replace_list = ['×', ';', "\n", "  "]
    result = string_data
    for repl in replace_list:
        result = result.replace(repl, " ")

    return result


def get_phones(phone_col):
    phones_list = []
    for phone in phone_col:
        phone_i = phone.text.replace(' ', '').replace('(', '').replace(')', '').replace('-', '').replace('+38', '')
        phones_list.append(phone_i)

    return ', '.join(phones_list)


def read_adverts_file():
    with open(file=f'links_{cur_date}.txt') as file:
        adverts = file.readlines()
        for adv in adverts:
            write_csv_file(parse_advert(url=adv.strip()))


def crop_pic(path_pic):
    # box = (left, upper, right, lower)
    box = (0, 0, 0, 35)
    img = Image.open(path_pic)
    im_crop_outside = ImageOps.crop(img, box)
    im_crop_outside.save(path_pic, quality=75)
    return path_pic


def save_photo(photo_col):
    photo_links_list_or = []
    photo_links_list = []
    for photo in photo_col:
        photo_link = photo.get('src').replace('.jpg', '_big.jpg')
        photo_links_list_or.append(photo_link)
        print(photo_link)
        img_data = requests.get(photo_link).content
        result = re.search(r'[\w-]+\.jpg', photo_link)
        photo_path = 'pics/' + result.group(0)
        with open(photo_path, 'wb') as handler:
            handler.write(img_data)
            time.sleep(1)

        photo_links_list.append(crop_pic(photo_path))

    return ', '.join(photo_links_list)


def write_csv_file(data):
    with open(file=f'data_{cur_date}.csv', mode='a', encoding='utf-8') as file:
        file.write(';'.join(data)+'\n')
        # writer.writerow(data)


def main():
    # replace link to needed directory of scraping
    # get_data(url='https://flagma.ua/products/uslugi-uborki-urozhaya/')
    read_adverts_file()


if __name__ == '__main__':
    main()
