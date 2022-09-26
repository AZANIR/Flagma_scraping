import random
import re
import time
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
        with open(file=f'links_{cur_date}.txt', mode='a') as file:
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
    # time.sleep(random.randint(2, 3))  # set timeout if we dont have parse items
    response = session.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    # title
    title = etree.HTML(str(soup)).xpath('//div[@class="card-m"]//h1')[0].text.strip()
    # title = '2'
    # description
    description = soup.find('div', id='description').text.strip()
    # contact name
    try:
        contact_name = etree.HTML(str(soup)).xpath('//div[@class="user-name"]')[0].text.strip()
    except:
        contact_name = etree.HTML(str(soup)).xpath('//div[@class="user-name"]/span')[0].text.strip()

    # company info
    company_info = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-info']//span")[
        0].text.strip()
    company_info_2 = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-info']//span")[
        1].text.strip()
    # count adv
    count_adv = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-ads-link']/a")[
        0].text.strip()
    # photo
    photo_links_list = []
    photo_col = soup.select('.card-m .small-photos-block img')
    for photo in photo_col:
        photo_link = photo.get('src').replace('.jpg', '_big.jpg')
        photo_links_list.append(photo_link)
        # print(photo_link) # if need download pics uncomment this block
        # download pics
        # img_data = requests.get(photo_link).content
        # result = re.search(r'[\w-]+\.jpg', photo_link)
        # print(result.group(0))
        # with open('pics/'+result.group(0), 'wb') as handler:
        #     handler.write(img_data)

    # phones
    phones_list = []
    phone_col = soup.select('a.tel')
    for phone in phone_col:
        phone_i = phone.text.replace(' ', '').replace('(', '').replace(')', '').replace('-', '').replace('+38', '')
        phones_list.append(phone_i)
        # print(phone_i)

    print(title)
    print(description)
    print(contact_name)
    print(company_info, company_info_2)
    print(count_adv)
    print(', '.join(photo_links_list))
    print(', '.join(phones_list))


def read_adverts_file():
    with open(file=f'links_{cur_date}.txt') as file:
        adverts = file.readlines()
        for adv in adverts:
            parse_advert(url=adv.strip())


def main():
    # replace link to needed directory of scraping
    get_data(url='https://flagma.ua/products/uslugi-uborki-urozhaya/')
    read_adverts_file()


if __name__ == '__main__':
    main()
