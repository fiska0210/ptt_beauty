import requests
import time
from bs4 import BeautifulSoup
import os
import re
import urllib.request
import json


PTT_URL = 'https://www.ptt.cc'


def get_web_page(url):
    time.sleep(0.5)  #time pause 
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html.parser')

    # get the previous page
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']

    articles = []  # store the article data 
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').string.strip() == date:  # check the posting date
            # get the number of 'push'
            push_count = 0
            if d.find('div', 'nrec').string:
                try:
                    push_count = int(d.find('div', 'nrec').string)  # convert string into int 
                except ValueError:  # if convert fail, donot do anything, pusu_count stay in 0
                    pass

            # get article url and title
            if d.find('a'):  # if(url) article exist 
                href = d.find('a')['href']
                title = d.find('a').string
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count
                })
    return articles, prev_url


def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls


def save(img_urls, title, counter):
    if img_urls:
        try:
            #dname = title.strip()  #  use strip() to delete the space' ' in the front and end of string
            dname = 'testfile' + str(counter)
            os.makedirs(dname)
            for img_url in img_urls:
                if img_url.split('//')[1].startswith('m.'):
                    img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg'):
                    img_url += '.jpg'
                fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(dname, fname))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    current_page = get_web_page('https://www.ptt.cc/bbs/Sex/index.html')
    folder_counter = 0
    if current_page:
        articles = []  # all articles today
        date = time.strftime("%m/%d").lstrip('0')  # date of today, remove '0' in front to match format of PTT 
        print("today is : " + date)        
        current_articles, prev_url = get_articles(current_page, date)  # today's articles in current page
        while current_articles:  # if adding today's articles in current page, back to previous pages and keeping search weather exist today's argicles
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, date)

        # got article-list and starting enter to each article and imgread
        for article in articles:
            print('Processing', article)
            folder_counter = folder_counter + 1
            page = get_web_page(PTT_URL + article['href'])
            if page:
                img_urls = parse(page)
                save(img_urls, article['title'], folder_counter)
                article['num_image'] = len(img_urls)

        # store article data
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)


