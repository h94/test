# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import shutil
import requests
import json

class OpenWeb(object):
    def __init__(self, send_msg, project_folder, driver_executable, site):
       self.send_msg = send_msg
       self.project_folder = project_folder
       self.driver_executable = driver_executable
       self.cdp_port = self.get_cdp_port(site)

    def open_web(self, url):
        """
        初始化瀏覽器，並回傳driver物件

        Args:
            url (str): "site url"

        Returns:
            driver (webdriver.Chrome): driver object
        """
        try:
            # self.close_driver()
            # options = webdriver.ChromeOptions()
            # options.add_argument("--disable-blink-features=AutomationControlled") #是否driver控制瀏覽器
            # options.add_experimental_option("excludeSwitches", ["enable-logging"]) #關閉除錯LOG(selenium自帶的,並非程式碼錯誤)

            # # 開啟debug設定，有兩種(看你用的driver lib是什麼，沒用到的那一個就刪掉)
            # # cdp不一定要開，driver有關不掉的問題在用
            # if self.cdp_port:
            #     options.add_argument(f"--remote-debugging-port={self.cdp_port}") #允許透過CDP進行監管(用來關殭屍chrome) selenium開這個
            #     options.debugger_address = f"127.0.0.1:{self.cdp_port}" #允許透過CDP進行監管(用來關殭屍chrome) undetected-chromedriver開這個

            # prefs = {"profile.managed_default_content_settings.images": 2}
            # options.add_experimental_option("prefs", prefs)
            # service = ChromeService(self.driver_executable)
            # try:
            #     driver = webdriver.Chrome(options=options, service=service)
            # except Exception as error:
            #     self.send_msg()
            #     #沒driver、driver跟chrome版本不符，都會下載對應版本後，把舊的砍掉在複製新的進去
            #     if any(kerword in str(error) for kerword in[
            #         "executable needs to be in PATH",
            #         "No such file or directory",
            #         "This version of ChromeDriver only supports",
            #         "Unable to obtain driver for chrome"
            #         ]):
            #         chrome_install = ChromeDriverManager().install()
            #         folder = os.path.dirname(chrome_install)
            #         chromedriver_path = os.path.join(folder, "chromedriver.exe")
            #         os.makedirs(self.project_folder, exist_ok=True)
            #         #有舊的先刪掉舊的
            #         if os.path.exists(self.driver_executable):  os.remove(self.driver_executable)
            #         time.sleep(2)
            #         shutil.copy2(chromedriver_path, self.driver_executable)
            #         time.sleep(2)
            #         os._exit(0)
            # driver.set_window_size(1000, 900)  #視窗大小
            # driver.implicitly_wait(10) #隱式等待(10秒)是在嘗試發現某個元素的時候，如果沒能立刻發現，就等待固定長度的時間，等時間到了還未發現則直接報錯.
            # driver.get(url)
            driver = None
            return driver
        except :
            self.send_msg()

    def close_driver(self):
        """
        用保險的方式關閉driver
        接在driver.quit()後面
        使用這個function需要開啟chrome debug port
        用cdp的好處是當chrome失去driver的控制時可以透過API進行關閉(也可以關閉別的進程開啟後沒有正常關掉的chrome)
        """
        # try:
        #     # Chrome 調試介面的 JSON 列表
        #     if self.cdp_port:
        #         tabs = requests.get(f'http://localhost:{self.cdp_port}/json', timeout=5).json()

        #         for tab in tabs:
        #             url = tab.get('url', '')
        #             title = tab.get('title', '')
        #             tab_id = tab.get('id', '')
        #             #把網址的xxxxx替換為網站的域名
        #             if 'https://xxxxx.com/' in url.lower():
        #                 print(f"關閉分頁：{title} ({url})")
        #                 requests.get(f"http://localhost:{self.cdp_port}/json/close/{tab_id}", timeout=5)
        #                 break
        # except Exception as e:
        #     pass

        # try:
        #     tasklist = os.popen('tasklist').read()
        #     #改成driver的名字
        #     if "xxxxxdriver.exe" in tasklist:
        #         os.system("taskkill /f /im xxxxxdriver.exe") #保險用  若quit()失敗時 由kill強制關閉
        # except:
        #     self.send_msg()

    def get_cdp_port(self, site):
        """
        從Z槽的crawler_cdp_setting.json取得站台的cdp port
        每個有用到cdp功能的爬蟲port都要用不一樣的，不能重複

        Args:
            site (_type_): stake

        Returns:
            int: cdp port
        """
        # try:
        #     file_path = r"Z:\crawler_cdp_setting.json"

        #     with open(file_path, "r", encoding="utf-8") as f:
        #         cdp_setting = json.load(f)  # 轉換成字典
        #     return cdp_setting.get(site)
        # except FileNotFoundError:
        #     raise FileNotFoundError(f"[cdp_port exception]找不到檔案：{file_path}")
        # except json.JSONDecodeError as e:
        #     raise json.JSONDecodeError(f"[cdp_port exception]JSON 格式錯誤: {e}")
        # except:
        #     self.send_msg()
        #     return None