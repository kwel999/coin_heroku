community_link = "http://aminoapps.com/c/Anime-Worlds"

proxies = {'http': 'socks5://212.156.216.185:8111','https':'socks5://212.156.216.185:8111'}


import concurrent.futures
from os import system, sys
from time import sleep
import threading
from colorama import Fore

print("\t\033[1;31m Super Fast         Heroku/replit Edition\n\n")
print('''
Subscribes to :  https://youtube.com/c/KWELATEYOURPIZZA
                Githube : https://github.com/kwel999
                discord : https://discord.gg/wGRQYd3nVd
''')
import os, json, time
import concurrent.futures
from os import system, sys
from time import sleep
import threading
from colorama import Fore

try:
    import samino, pyfiglet
except:
    os.system('pip install samino -U')
    os.system('pip install pyfiglet')
    import samino, pyfiglet
else:
    os.system('clear')
    A = '\x1b[1;91m'
    Z1 = '\x1b[2;31m'
    E = '\x1b[1;92m'
    H = '\x1b[1;93m'
    L = '\x1b[1;95m'
    B = '\x1b[2;36m'
    Y = '\x1b[1;34m'
    M = '\x1b[1;94m'

  


    def tzr():
        localhour = time.strftime('%H', time.gmtime())
        localminute = time.strftime('%M', time.gmtime())
        UTC = {'GMT0':'+0',  'GMT1':'+60',  'GMT2':'+120',  'GMT3':'+180',  'GMT4':'+240',  'GMT5':'+300',  'GMT6':'+360',  'GMT7':'+420',  'GMT8':'+480',  'GMT9':'+540',  'GMT10':'+600',  'GMT11':'+660',  'GMT12':'+720',  'GMT13':'+780',  'GMT-1':'-60',  'GMT-2':'-120',  'GMT-3':'-180',  'GMT-4':'-240',  'GMT-5':'-300',  'GMT-6':'-360',  'GMT-7':'-420',  'GMT-8':'-480',  'GMT-9':'-540',  'GMT-10':'-600',  'GMT-11':'-660'}
        hour = [
         localhour, localminute]
        if hour[0] == '00':
            tz = UTC['GMT-1']
            return int(tz)
        if hour[0] == '01':
            tz = UTC['GMT-2']
            return int(tz)
        if hour[0] == '02':
            tz = UTC['GMT-3']
            return int(tz)
        if hour[0] == '03':
            tz = UTC['GMT-4']
            return int(tz)
        if hour[0] == '04':
            tz = UTC['GMT-5']
            return int(tz)
        if hour[0] == '05':
            tz = UTC['GMT-6']
            return int(tz)
        if hour[0] == '06':
            tz = UTC['GMT-7']
            return int(tz)
        if hour[0] == '07':
            tz = UTC['GMT-8']
            return int(tz)
        if hour[0] == '08':
            tz = UTC['GMT-9']
            return int(tz)
        if hour[0] == '09':
            tz = UTC['GMT-10']
            return int(tz)
        if hour[0] == '10':
            tz = UTC['GMT13']
            return int(tz)
        if hour[0] == '11':
            tz = UTC['GMT12']
            return int(tz)
        if hour[0] == '12':
            tz = UTC['GMT11']
            return int(tz)
        if hour[0] == '13':
            tz = UTC['GMT10']
            return int(tz)
        if hour[0] == '14':
            tz = UTC['GMT9']
            return int(tz)
        if hour[0] == '15':
            tz = UTC['GMT8']
            return int(tz)
        if hour[0] == '16':
            tz = UTC['GMT7']
            return int(tz)
        if hour[0] == '17':
            tz = UTC['GMT6']
            return int(tz)
        if hour[0] == '18':
            tz = UTC['GMT5']
            return int(tz)
        if hour[0] == '19':
            tz = UTC['GMT4']
            return int(tz)
        if hour[0] == '20':
            tz = UTC['GMT3']
            return int(tz)
        if hour[0] == '21':
            tz = UTC['GMT2']
            return int(tz)
        if hour[0] == '22':
            tz = UTC['GMT1']
            return int(tz)
        if hour[0] == '23':
            tz = UTC['GMT0']
            return int(tz)


    def trr():
        return [{'start':int(time.time()),  'end':int(time.time() + 300)} for _ in range(50)]


    from flask import Flask
    from threading import Thread
    import random
    app = Flask('')

    @app.route('/')
    def home():
        return 'Bot on'


    def run():
        app.run(host='0.0.0.0', port=(random.randint(2000, 9000)))


    def keep_alive():
        t = Thread(target=run)
        t.start()


    keep_alive()
    client = samino.Client(proxies=proxies, deviceId = "42018060F4195790EE4AF93B2E844F46635DFABA92CF933D1CDC5F8AE8CDC00BC1FFAA1205BC2FF172")
    com = client.get_from_link(community_link).comId
    file = open('acc.json')
    date = json.load(file)

    def threadit(email: str, password: str, device: str):
        try:
            client.login(email, password)
            time.sleep(10)
            client.join_community(com)
            local = samino.Local(com)
            print(H + '\nlogin done')
            for q in range(24):
                local.send_active_time(tz=(tzr()), timers=(trr()))
                print(A + f"{q + 1} Coin Generating - OK")
                time.sleep(30)
            else:
                print(H + '\nCoins Genarated !! ')

        except Exception as e:
            try:
                print(e)
            finally:
                e = None
                del e


    def main():
        for acc in date:
            email = acc['email']
            password = acc['password']
            device = acc['device']
            threadit(email=email, password=password, device=device)


    if __name__ == '__main__':
                main()
