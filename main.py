# -*- coding: utf-8 -*- 

__project__ = "profile_follower_chain"
__version__ = "1.0.0"
__author__ = "Mefamex"
__email__ = "info@mefamex.com"
__url__ = "https://mefamex.com/projects/profile_follower_chain/"
__license__ = "MIT"
__description__ = "Kullanıcıların takipçi ve takip edilenlerini analiz eden bir Python projesidir. Kullanıcılar, belirli bir hesabın sosyal ağını keşfederek takipçi ve takip edilenlerin listesini çıkarabilir."
__url_github__ = "https://github.com/mefamex/profile_follower_chain"
__status__ = "Production"
__date__ = "2025-02-07"
__date_modify__ = "2025-02-07"
__python_version__ = ">=3.13" 
__dependencies__ = {}

___doc___ = """
Proje Adi: Profile Follower Chain
Yazar: Ad (posta@posta.com) (https://web_sitesi.com)
Lisans: MIT

Aciklama:
Kullanıcıların takipçi ve takip edilenlerini analiz eden bir Python projesidir. Kullanıcılar, belirli bir hesabın sosyal ağını keşfederek takipçi ve takip edilenlerin listesini çıkarabilir.

Ozellikler: 
    - Belirli bir GitHub kullanıcısının takipçi ve takip edilenlerini çekme.
    - Takipçi ve takip edilenlerin listesini derinlemesine analiz etme.
    - Kullanıcılar arasındaki ilişkileri görselleştirme.
    - Kullanıcıların sosyal ağlarını genişletmelerine yardımcı olma.

Moduller: ...
Siniflar: ...
Fonksiyonlar: ...
Kullanim: ...

Kurulum:
    - Proje klonlama: ...
    - Gerekli bağimliliklari kurma: ...
    - Proje calistirma: ...

Tarihce:
- 1.0.0 (2024-02-03): Basla

Sorumluluk Reddi: 
    Bu yazilim "olduğu gibi" sunulmaktadir. Yazar, bu yazilimin kullanimi sonucunda ortaya cikan herhangi bir zarardan sorumlu değildir.
"""


import os,sys,subprocess, requests
from flask import Flask, render_template, request, jsonify
from time import sleep
from datetime import datetime, timedelta

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


from flask import Flask, render_template, request
print("imported dependencies")

Profiles: dict[str, 'PROFILE'] = {}  # Type-annotated global dictionary

class PROFILE:
    
    def __init__(self, nick: str = "") -> None:
        nick = nick.lower().strip()
        if not nick: raise ValueError("Nickname cannot be empty")
            
        if nick not in Profiles:
            self.done: int = 0  # 0=init, 1=info loaded, 2=relationships loaded
            self.nick: str = nick
            self.name: str = ""
            self.bio: str = ""
            self.followers: dict[str, 'PROFILE'] = {}
            self.following: dict[str, 'PROFILE'] = {}
            self.followers_count: int = 0
            self.following_count: int = 0
            self.url_profile: str = f"https://github.com/{nick}/"
            self.url_followers: str = f"{self.url_profile}followers"
            self.url_following: str = f"{self.url_profile}following"
            Profiles[self.nick] = self
        else:
            self.__dict__.update(Profiles[nick].__dict__)

    def __repr__(self) -> str: return f"PROFILE('{self.nick}')"
        
    def AddFollower(self, profile: 'PROFILE') -> None:
        if not isinstance(profile, PROFILE):raise ValueError("Profile must be PROFILE instance")
        if profile.nick not in self.followers: self.followers[profile.nick] = profile
        if self.nick not in profile.following: profile.following[self.nick] = self
    
    def AddFollowing(self, profile: 'PROFILE') -> None:
        if not isinstance(profile, PROFILE):raise ValueError("Profile must be PROFILE instance")
        if profile.nick not in self.following: self.following[profile.nick] = profile
        if self.nick not in profile.followers: profile.followers[self.nick] = self
            
    def printOne(self) -> None:
        print(f"Profile : {self.nick}")
        print(f"Status  : {'Complete' if self.done == 2 else 'Incomplete ('+str(self.done)+"/3)"}")
        print(f"Name    : {self.name}")
        print(f"Bio     : {self.bio}")
        print(f"follow_A: {self.followers_count}/{self.following_count}")
        print(f"follow_L: {len(self.followers)}/{len(self.following)}")
        print(f"Followers: {', '.join(self.followers.keys())}")
        print(f"Following: {', '.join(self.following.keys())}")

def printAll():
    print("\n\n\n\n#################################\nPRINTALL\n#######################")
    for q in Profiles:
        print("")
        Profiles[q].printOne()
        print("")

class FollowerChain:
    """Takipçi zincirini yönetir."""
    
    _url_follower:str="?tab=followers"
    _url_following:str="?tab=following"
    _website : str = "https://github.com/"
    
    def __init__(self, username:str):
        self.username :str = username.lower().strip()
        self.profile  :PROFILE= Profiles.get(username)
        if self.profile is None : 
            self.profile = PROFILE(username)
            Profiles[self.username] = self.profile

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.browser = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        print("[followerChain] init ok!")
    
    def start(self):
        self.load_user_info()
        self.loadFollowers()
        
    def load_user_info(self):
        if self.profile.done == 1 : return None
        print("[followerChain] load user info:", self.profile.url_profile)
        self.browser.get(self.profile.url_profile)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "avatar-user")))
        self.profile.name = self.browser.find_elements(By.CLASS_NAME, "p-name")[0].text
        print("name:",self.profile.name,"\nnick:",self.profile.nick,end=", ", flush=True)
        self.profile.bio = self.browser.find_elements(By.CLASS_NAME, "js-user-profile-bio")[0].text
        print(self.profile.bio)
        _nick = self.browser.find_elements(By.CLASS_NAME, "p-nickname")[0].text.lower().strip()
        if _nick != self.profile.nick :
            print("WARNING   : new:",_nick," old:",self.profile.nick)
            self.profile.nick = _nick
        self.profile.followers_count = self.browser.find_elements(By.CSS_SELECTOR, "span[class='text-bold color-fg-default']")[0].text.strip()
        self.profile.following_count = self.browser.find_elements(By.CSS_SELECTOR, "span[class='text-bold color-fg-default']")[1].text.strip()
        print("count:", self.profile.followers_count, self.profile.following_count)
        self.profile.done=1
        
    def loadFollowers(self):
        if self.profile.done <1:self.load_user_info()
        elif self.profile.done == 2 : return None
        print("[followerChain] load followers:", self.profile.url_profile+self._url_follower)
        self.browser.get(self.profile.url_profile+self._url_follower)
        WebDriverWait(self.browser, 50).until(EC.presence_of_element_located((By.CLASS_NAME, "avatar-user")))
        followers = self.browser.find_elements(By.XPATH, "//span[contains(@class, 'Link--secondary') and contains(@class, 'pl-1')]")
        for item in followers:
            username = item.text.strip()
            if username:
                print("follower::::::", username)
                self.profile.AddFollower(PROFILE(username))
        print("[followerChain] load following:", self.profile.url_profile+self._url_follower)
        self.browser.get(self.profile.url_profile+self._url_following)
        WebDriverWait(self.browser, 50).until(EC.presence_of_element_located((By.CLASS_NAME, "avatar-user")))
        self.profile.following = {}
        following = self.browser.find_elements(By.XPATH, "//span[contains(@class, 'Link--secondary') and contains(@class, 'pl-1')]")
        for item in following:
            username = item.text.strip()
            if username:
                print("following::::", username)
                self.profile.AddFollowing(PROFILE(nick=username))
        self.profile.done=2





class open_in_browser:
    _host : str = "127.0.0.1"
    _port : int = 5000
    
    def __init__(self, host:str=_host, port:int=_port):
        self._host = host 
        self._port = port
        self.app = Flask(__name__, template_folder='templates')
        self.message = "Merhaba"
        self.page_called = 0
        self.username=""
        self.start()
    
    def start(self):
        print(f"[-info-] Starting browser Running on http://{self._host}:{self._port}")
        self.init_routes()
        self.app.run(host=self._host, port=self._port, debug=True)
        
    def init_routes(self):
        @self.app.route('/', methods=['GET', 'POST'])
        def home():
            if request.method == "POST":
                print("POST")
                
                self.message = "Yalnızlık güzeldir.."
                #print(request.form)  # Print form data
                #for key, value in request.form.items():print(f"{key}: {value}")
                print("data:", request.data)
                if len(request.json['param'])>0:
                    self.username = request.json['param'].replace(' ', '_')
                    self.message += "\n" + str(self.username)
            else:
                print("GET")
                self.page_called+=1
            return render_template('index.html', message=self.message , page_called=self.page_called, username=self.username)
        
        @self.app.errorhandler(404)
        def page_not_found(e):
            print("PAGE_NOT_FOUND()")
            return render_template('404.html', e=str(e)), 404
    

def main():
    FollowerChain().start()
    printAll()
    for q in Profiles.copy().keys():
        FollowerChain(q).start()
    printAll()
    exit()
    browser  = open_in_browser()

print("main.py : touched . name =",__name__)
if __name__ == "__main__":
    print(  f"\n- - - - - - - - - - - - - - - - - - - - - - -\n"+
            f"#############################################\n"+
            f"##                                         ##\n"+
            f"##           FOLLOWER CHAIN                ##\n"+
            f"##                                         ##\n"+
            f"#############################################\n"+
            f"###### INFORMATION OF RUNNING THIS FİLE ######\n"+
            f"Current Script: {__file__}\n"+ 
            f"Python Version: {sys.version}\n"+ 
            f"Python Path   : {sys.path[-1]}\n"+ 
            f"Current Dir   : {os.getcwd()}\n"+
            f"Command Args  : {sys.argv}\n"+
            f"Project       : {__project__}\n"+
            f"#############################################\n"+
            f"#############################################\n"+
            f"#############################################\n")
    main(username="mefamex")
    print(  f"#############################################\n"+
            f"##                                         ##\n"+
            f"##              RUN OVER                   ##\n"+
            f"##                                         ##\n"+
            f"#############################################\n")
