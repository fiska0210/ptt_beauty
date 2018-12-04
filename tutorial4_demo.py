import requests
import time
from bs4 import BeautifulSoup
import os
import re
import urllib.request
import json
import shutil
import sys
import codecs


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
            global push_count 
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


def save(img_urls, title, times, datapath): #nooooot yet!
    if img_urls:
        try:
            #dname = title.strip()  #  use strip() to delete the space' ' in the front and end of string
            dname = 'file' + str(times)
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
            read_floder(datapath,times)
        except Exception as e:
            print(e)
    print("final done!!!")


def lineNotify(msg, picURI):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + "06OrDKN9pqYaTIe7dYaA26bmiStbUCRvzDc5ZVulCNT"
    }
    #line_api_test : 06OrDKN9pqYaTIe7dYaA26bmiStbUCRvzDc5ZVulCNT
   
    payload = {'message': msg}
    files = {'imageFile': open(picURI, 'rb')}
    r = requests.post(url, headers = headers, params = payload, files = files)
    #r = requests.post(url, headers = headers, files = files)
    return r.status_code
    print("api done!")
 
def read_floder(datapath,times):
    print("read fresh folder!")
    # print(datapath)

    for dirname, dirnames, filenames in os.walk('.'):
        for f in filenames:
            #print("times :" + str(dirname[7]))
            if str(dirname[2:7]) == "file"+str(times) :
                print("tset " + str(dirname[2:7]))
                # if dirname[7] == time : 
                filepath = str(dirname) + "/" + str(f)
                print(filepath)
                msg = 'https://www.ptt.cc/' + str(datapath)
                # lineNotify(msg, filepath)

                print("send to line!") 


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    current_page = get_web_page('https://www.ptt.cc/bbs/Beauty/index.html')
    token = "06OrDKN9pqYaTIe7dYaA26bmiStbUCRvzDc5ZVulCNT"
    times = 0
    read = []
    with open('record.txt') as f:
        for each_line in f :
                #a = each_line.split("\n")
                #read.append(str(each_line.split("\n")))
            read = each_line.split(",")
        # print(each_line)
        print(read)
    

    if current_page:
        articles = []  # all articles today
        date = time.strftime("%m/%d").lstrip('0')  # date of today, remove '0' in front to match format of PTT 
        # print(date)
        # date = '10/12'        
        current_articles, prev_url = get_articles(current_page, date)  # today's articles in current page
        
        while current_articles:  # if adding today's articles in current page, back to previous pages and keeping search weather exist today's argicles
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, date)
           

        # got article-list and starting enter to each article and imgread
        with open('record.txt', 'w') as w :
            for i in range(len(read)) : 
                w.write(read[i] + ',')
                # w.write("\n")

            for article in articles:
                datapath = article['href']
                push_counter = article['push_count']
                # print(datapath)
                # print(push_counter)
                if datapath not in read : 
                    w.write(datapath + ',')
                    # w.write("\n")
                    # print('Processing', article)
                    
                    # datapath = article['href']
                    #rprint(datapath)
                    
                    
                    page = get_web_page(PTT_URL + article['href'])
                    # print(page)
                    if page:
                        img_urls = parse(page)
                        if push_counter > 20 :
                            print("push = " + str(push_counter))
                            # save(img_urls, article['title'], times, datapath)  !!!!!!!should open
                            # print("title")
                            # print(article['title'])
                            times = times + 1
                            article['num_image'] = len(img_urls)
                        else : 
                           continue


        # store article data
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)


