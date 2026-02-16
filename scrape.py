import os
try:
 import requests
 from time import sleep
 from configparser import ConfigParser
 from os import system, name
 from threading import Thread, active_count
 from re import search, compile
except:
 os.system('pip install requests')
 os.system('pip install configparser')
THREADS = 500
PROXIES_TYPES = ('http', 'socks4', 'socks5')
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
REGEX = compile(r"(?:^|\D)?(("+ r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
                + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
                + r")(?:\D|$)")

errors = open('errors.txt', 'a+')
cfg = ConfigParser(interpolation=None)
cfg.read("config.ini", encoding="utf-8")

http, socks4, socks5 = '', '', ''
try: http, socks4, socks5 = cfg["HTTP"], cfg["SOCKS4"], cfg["SOCKS5"]
except KeyError: print(' [ OUTPUT ] Error | config.ini not found!');sleep(3);exit()

http_proxies, socks4_proxies, socks5_proxies = [], [], []
time_out = 15

def save_proxies(proxies, proxy_type):
    with open(f"{proxy_type}_proxies.txt", 'w') as file:
        for proxy in proxies:
            file.write(proxy + '\n')

def scrap(sources, _proxy_type):
    proxies = []
    for source in sources:
        if source:
            try:
                response = requests.get(source, timeout=time_out)
                if tuple(REGEX.finditer(response.text)):
                    for proxy in tuple(REGEX.finditer(response.text)):
                        proxies.append(proxy.group(1))
            except Exception as e:
                errors.write(f'{e}\n')

            if _proxy_type == 'http':
                save_proxies(proxies, 'http')
            elif _proxy_type == 'socks4':
                save_proxies(proxies, 'socks4')
            elif _proxy_type == 'socks5':
                save_proxies(proxies, 'socks5')

def start_scrap():
    threads = []
    for i in (http_proxies, socks4_proxies, socks5_proxies): i.clear()
    for i in ((http.get("Sources").splitlines(), 'http'), (socks4.get("Sources").splitlines(), 'socks4'), (socks5.get("Sources").splitlines(), 'socks5')):
        thread = Thread(target=scrap, args=(i[0], i[1]))
        threads.append(thread)
        thread.start()
    for t in threads: t.join()
    
def start_view():
    c, threads = 0, []
    start_scrap()
    

Thread(target=start_view).start()