#!/usr/bin/python3
from io import BytesIO
from datetime import datetime
import shutil
import requests
import re
import json
import os
import getpass

s = requests.session()

default_headers = {'Host': 'claco.vinci.be',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                   'Upgrade-Insecure-Requests': '1',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Referer': 'http://claco.vinci.be/desktop/tool/open/resource_manager',
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4,nl;q=0.2,es;q=0.2'}

ressources_headers = {'Host': 'claco.vinci.be',
                      'Connection': 'keep-alive',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                      'Accept': '*/*',
                      'X-Requested-With': 'XMLHttpRequest',
                      'X_Requested_With': 'XMLHttpRequest',
                      'Referer': 'http://claco.vinci.be/desktop/tool/open/resource_manager',
                      'Accept-Encoding': 'gzip, deflate, sdch',
                      'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4,nl;q=0.2,es;q=0.2'}

login_headers = {'Host': 'claco.vinci.be',
                 'Connection': 'keep-alive',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                 'Upgrade-Insecure-Requests': '1',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'Origin': 'http://claco.vinci.be',
                 'Cache-Control': 'max-age=0',
                 'Content-Length': '80',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                 'Referer': 'http://claco.vinci.be/login',
                 'Accept-Encoding': 'gzip, deflate',
                 'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4,nl;q=0.2,es;q=0.2'}


def getPhpsesid(s):
    try:
        url = 'http://claco.vinci.be'
        headers = default_headers
        r = s.get(url, headers=headers)
    except Exception as e:
        print(str(e))
    return


def login(s, username, password):
    getPhpsesid(s)

    try:
        print('Connecting...')
        url = 'http://claco.vinci.be/login_check'

        value = {'_username': username, '_password': password, '_remember_me': 'on'}

        r = s.post(url, headers=login_headers, data=value, allow_redirects=True)

        if r.url == 'http://claco.vinci.be/login':
            print('E-mail ou password invalide')
            return False
        else:
            print('Connected !')
            return True

    except Exception as e:
        print(str(e))
    return False


def download(s, id, path):
    try:
        # Build the url with ressources id
        url = 'http://claco.vinci.be/resource/download?ids%5B%5D=' + str(id)

        # Do the request and display the text
        print('X -', path, end=' ')
        print('Downloading... ', end='')
        r = s.post(url, headers=default_headers, allow_redirects=False)
        print(r.status_code)

        if r.status_code == 200:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            out_file = open(path, "wb")
            shutil.copyfileobj(BytesIO(r.content), out_file)
            out_file.close

    except Exception as e:
        print(str(e))

    return


def getDifference(s, dir):
    # Build url with id
    url = 'http://claco.vinci.be/resource/directory'
    if dir:
        url += '/' + str(dir)

    # Do the request
    r = s.get(url, headers=ressources_headers)

    # Take all files or directories from the json
    jsondata = json.loads(r.text)['nodes']

    # Browse the list
    for res in jsondata:

        # if it's a file
        if res['type'] == 'file':
            path = res['path_for_display']
            path = re.sub(' +\/ +', '/', path)
            path = re.sub(r'[<|>|?|$|!|:|*]', r'_', path)
            clacoModifDate = datetime.strptime(res['modification_date'], '%d/%m/%Y %H:%M:%S')
            try:
                localCreaDate = datetime.fromtimestamp(os.stat(path).st_ctime)
                if clacoModifDate > localCreaDate:
                    download(s, res['id'], path)
                else:
                    print('V -', path)
            except OSError:
                download(s, res['id'], path)
        # if it's a directory
        if res['type'] == 'directory':
            getDifference(s, res['id'])
    return


username = input('E-mail :')
password = getpass.getpass()

if login(s, username, password):
    getDifference(s, None)
