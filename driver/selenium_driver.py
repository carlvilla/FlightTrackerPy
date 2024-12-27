import random
import urllib
import pickle
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def setting_up_selenium():
    try:
        print("Setting up Selenium driver...")
        
        agents = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")            
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(' - user-agent=' + random.choice(agents) + '"') # Set browser’s user agent
        options.add_argument("--incognito") # Setting incognito mode

        driver_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(options=options, service=ChromeService(driver_path))

        return driver
    except Exception as e:
        print(e)
        print("An error occurred while setting the Selenium driver...")
        #subprocess.call(['osascript', '-e', 'tell application "Tor Browser" to quit'])
        #return self.setting_up_selenium()

def safe_cookies(driver):
    print("Saving cookies...")
    pickle_filename = "cookies.pkl"
    pickle.dump(driver.get_cookies(), open(pickle_filename, "wb"))

def get_proxy():
    prox = Proxy()
    try:
        # Select a random proxy
        idx_proxy = random.randint(0, len(self.proxies))
        proxy_data = self.proxies[idx_proxy]

        print(proxy_data)

        proxy_ip = proxy_data['IP Address']
        proxy_port = proxy_data['Port']
        proxy_country = proxy_data['Country']
        prox.ip = proxy_ip
        prox.proxy_type = ProxyType.MANUAL
        prox.http_proxy = proxy_ip + ":" + proxy_port
        print("Trying to connect with proxy", proxy_ip, "from", proxy_country)
        proxy_handler = urllib.request.ProxyHandler({'https': proxy_ip + ":" + proxy_port})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req = urllib.request.Request('http://www.example.com')
        urllib.request.urlopen(req)
        print("Proxy seems to be working!")
    except Exception:
        print("Connection error! (Trying another proxy)")
        return self.get_proxy()
    return prox