import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
from path import find_exe_path
import subprocess
import pygetwindow as gw


def get_driver():
    service=Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=service,options=options)

def search_google(query):
    driver=get_driver()
    driver.get("https://www.google.com")
    time.sleep(2)
    search_box=driver.find_element(By.NAME,"q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(20)
    driver.quit()

def play_youtube(query):
    driver=get_driver()
    driver.get("https://www.youtube.com")
    time.sleep(3)
    search_box=driver.find_element(By.NAME,"search_query")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    video_results=driver.find_elements(By.ID,"video-title")
    if video_results:
        video_results[0].click()
    else:
        print("No video results found")
    while True:
        state=driver.execute_script("return document.querySelector('video').ended;")
        if state:
            print("Video ended")
            break
        time.sleep(5)
def open_website(query):
    words=query.split()
    for word in words:
        if "." in word:
            driver=get_driver()
            driver.get("https://"+word)
            time.sleep(100)
            driver.quit()
            return

def open_app(app_keyword,text=None):
    path=find_exe_path(app_keyword)
    if path:
        subprocess.Popen(path)
        target_window=None
        for i in range(20):
            matches=[win for win in gw.getAllTitles() if app_keyword.lower() in win.lower()]
            if matches:
                try:
                    target_window=gw.getWindowsWithTitle(matches[0])[0]
                    target_window.activate()
                    break
                except Exception as e:
                    print(f"couldn't find active window: {e}")
            time.sleep(0.25)
        time.sleep(1)

        if text:
            pyautogui.write(text)
            print(f"Types:{text}")
    else:
        print(f"Could not locate app matching: {app_keyword}")

