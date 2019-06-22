#!/usr/bin/python
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


def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls


def save(img_urls, title, datapath): #nooooot yet!
    if img_urls:
        try:
            #dname = title.strip()  #  use strip() to delete the space' ' in the front and end of string
            dname = 'RedVelvet'
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
            read_floder(datapath)
        except Exception as e:
            print(e)
    print("final done!!!")


def lineNotify(msg, picURI):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + "dE4IOzy2FeQlCi07qtedf03wSkIQFBknbBl09kuDQXp"
    }
    #line_api_test : 06OrDKN9pqYaTIe7dYaA26bmiStbUCRvzDc5ZVulCNT
   
    payload = {'message': msg}
    files = {'imageFile': open(picURI, 'rb')}
    r = requests.post(url, headers = headers, params = payload, files = files)
    return r.status_code
    print("api done!")
 
def read_floder(datapath):
    print("read fresh folder!")

    for dirname, dirnames, filenames in os.walk('.'):
        for f in filenames:
            if str(dirname[2:11]) == "RedVelvet" :
                filepath = str(dirname) + "/" + str(f)
                msg = 'https://www.ptt.cc' + str(datapath)
                lineNotify(msg, filepath)
                print("send to line!") 


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    current_page = get_web_page('https://www.ptt.cc/bbs/RedVelvet/index.html')
    token = "dE4IOzy2FeQlCi07qtedf03wSkIQFBknbBl09kuDQXp"
    times = 0
    read = []
    os.system("rm -rf Red*")
    

        
    datapath = '/bbs/RedVelvet/M.1544262969.A.326.html'
    
    print(datapath)
    print('Processing')
    
    page = get_web_page(PTT_URL + datapath)
    if page:
        img_urls = parse(page)
        times = 1
        save(img_urls, datapath, datapath)  #!!!!!!!should open
        

