import re, os
from time import sleep
from bs4 import BeautifulSoup
import sys
import json
import random
import requests

def get_SID(url):
    SID = None
    sids = re.split('[?&]', url)
    for sid in sids:
        if 'SID' in sid:
            SID = sid.strip().split('=')[1]
            break
    if not SID:
        print('SID error')
        exit()
    return SID

def new_session():
    print('new session')
    s = requests.Session()
    s.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,de;q=0.8,en-US;q=0.6,zh-TW;q=0.4,zh;q=0.2,zh-CN;q=0.2,af;q=0.2',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    })
    resp = s.get('http://apps.webofknowledge.com/')
    SID = get_SID(resp.request.url)
    refer_url = 'http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&SID={}&search_mode=GeneralSearch'.format(SID)
    s.get(refer_url)
    return s, SID, refer_url

def set_data(SID, name, add):
    return {
        "fieldCount": 2,
        "action":"search",
        "product":"UA",
        "search_mode":"GeneralSearch",
        "SID": SID,
        "max_field_count":25,
        "max_field_notice":"Notice: You cannot add another field.",
        "input_invalid_notice":"Search Error: Please enter a search term.",
        "exp_notice":"Search Error: Patent search term could be found in more than one family (unique patent number required for Expand option)",
        "input_invalid_notice_limits": "<br/>Note: Fields displayed in scrolling boxes must be combined with at least one other search field.",
        "sa_params":"WOS||{}|http://apps.webofknowledge.com:443|'".format(SID),
        "formUpdated":"true",
        "value(input1)": name,
        "value(select1)":"AU",
        "value(hidInput1)": "",
        "value(bool_1_2)": "AND",
        "value(input2)": add,
        "value(select2)":"AD",
        "x": random.randint(764, 836),
        "y": random.randint(281, 300),
        "value(hidInput2)": "",
        "limitStatus":"collapsed",
        "ss_lemmatization":"On",
        "ss_spellchecking":"Suggest",
        "SinceLastVisit_UTC":"",
        "SinceLastVisit_DATE":"",
        "period":"Range Selection",
        "range":"ALL",
        "startYear":1900,
        "endYear":2017,
        "update_back2search_link_param":"yes",
        "ssStatus":"display:none",
        "ss_showsuggestions":"ON",
        "ss_numDefaultGeneralSearchFields":1,
        "ss_query_language":"auto",
        "rs_sort_by":"PY.D;LD.D;SO.A;VL.D;PG.A;AU.A"
    }


def one_user(s, SID, refer_url, name, add):
    print(name)
    print(add)
    data = set_data(SID, name, add)
    headers = {
        'Host': 'apps.webofknowledge.com', 
        'Origin': 'http://apps.webofknowledge.com', 
        'Referer': refer_url,
    }
    resp = s.post("http://apps.webofknowledge.com/UA_GeneralSearch.do", data = data, headers = headers)
    _SID = get_SID(resp.request.url)
    if _SID != SID:
        print(resp.request.url)
        return 1

    links = set()
    bsobj = BeautifulSoup(resp.text, "html.parser")

    try:
        url = bsobj.find('a', attrs = {'class': 'paginationNext'}).get('href')
    except:
        if 'Your search found no records.' in resp.text:
            return 2
        return 1

    for link in bsobj.find_all('div', attrs = {'class': 'search-results-content'}):
        links.add(link.find('a')['href'])

    while url and 'javascript' not in url:
        print(url)
        resp = s.get(url)
        _SID = get_SID(resp.request.url)
        if _SID != SID:
            print(resp.request.url)
            return 1
        bsobj = BeautifulSoup(resp.text, "html.parser")
        for link in bsobj.find_all('div', attrs = {'class': 'search-results-content'}):
            links.add(link.find('a')['href'])
        url = bsobj.find('a', attrs = {'class': 'paginationNext'}).get('href')
    
    res = {}
    for link in links:
        print(link)
        resp = s.get('http://apps.webofknowledge.com{}'.format(link))
        if get_SID(resp.request.url) != SID: 
            print(resp.request.url)
            return 1
        bsobj = BeautifulSoup(resp.text, "html.parser")
        try:
            adds = bsobj.find_all('table', attrs = {'class': 'FR_table_noborders'})[-1].find_all('td', attrs = {'class': 'fr_address_row2'})
        except IndexError:
            continue
        for add in adds:
            try:
                text = add.find('preferred_org').text
            except AttributeError:
                continue
            res[text] = res.get(text, 0) + 1
    print(res)
    return res

tasks = {}
with open('all_clear') as fo:
    for line in fo:
        _parts = re.split(';', line.strip())
        if len(_parts) != 3:
            logging.info("{} is wrong.".format(parts[0]))
            exit()
        tasks[_parts[0]] = _parts[1], _parts[2]

s, SID, refer_url = new_session()
#res = {}
count = 1
for id in tasks:
    name, add = tasks[id]
    fp = 'op/{}'.format(id)
    efp = 'error/{}'.format(id)
    nfp = 'none/{}'.format(id)
    if os.path.exists(fp) or os.path.exists(efp) or os.path.exists(nfp):
        continue

    _res = one_user(s, SID, refer_url, name, add)
    if _res == 1:
        sleep(10)
        s, SID, refer_url = new_session()
    elif _res == 2:
        with open(efp, 'w') as fo:
            fo.write('non-found')
    elif _res:
        with open(fp, 'w') as fo:
            for org in _res:
                fo.write('{};{};{};{}\n'.format(name, add, org, _res[org]))
    else:
        with open(nfp, 'w') as fo:
            fo.write('no-content')
    print(count, len(tasks), sep = '-------------')
    count += 1
