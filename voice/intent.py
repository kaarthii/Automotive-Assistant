import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
from path import find_exe_path
import subprocess
import pygetwindow as gw
from bs4 import BeautifulSoup


def get_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    return webdriver.Chrome(service=service, options=options)

def search_google(query):
    driver = None
    try:
        driver = get_driver()
        driver.get("https://www.google.com")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        max_wait = 180
        check_interval = 5
        elapsed = 0
        snippet = None
        captcha_detected = False

        while elapsed < max_wait:
            time.sleep(check_interval)
            elapsed += check_interval
            print(f"waiting...{elapsed}s")

            try:
                page_source = driver.page_source
            except Exception as e:
                print(f"Browser was closed by the user. Error: {e}")
                return "Browser was closed before data could be extracted."

            if "captcha" in page_source.lower() or "unusual traffic" in page_source.lower():
                if not captcha_detected:
                    print("CAPTCHA detected! Please solve it in the browser window.")
                    captcha_detected = True
                continue

            soup = BeautifulSoup(page_source, "html.parser")

            selectors = [
                "div.BNeawe.iBp4i.AP7Wnd",    #captures short, direct answers        
                "div.BNeawe.tAd8D.AP7Wnd",    #captures summaries of long text
                "div.BNeawe.s3v9rd.AP7Wnd",   #captures descriptive text 
                "div.kCrYT > a",              #captures anchor tags inside div containers        
                "div.ZINbbc.xpd.O9g5cc.uUPGi" #captures full result block
            ]

            for sel in selectors:
                elements = soup.select(sel)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text.split()) > 3:
                        snippet = text
                        print(f"Snippet found: {snippet}")
                        break
                if snippet:
                    break

            if not snippet:
                title_elem = soup.select_one("h3")
                if title_elem:
                    snippet = title_elem.get_text(strip=True)
                    print(f"Using top result title: {snippet}")

            if snippet:
                break

        return snippet if snippet else "Sorry, I couldn't find a readable answer."

    except Exception as e:
        print(f"Failed to extract snippet: {e}")
        return "Sorry, I couldn't fetch that information from Google."

            
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

def play_in_spotify(track_name):
    driver = get_driver()
    driver.get("https://open.spotify.com/search")
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-testid='search-input']"))
        )
        
        try:
            accept_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]"))
            )
            accept_btn.click()
        except:
            pass  

       
        search_input = driver.find_element(By.XPATH, "//input[@data-testid='search-input']")
        search_input.clear()
        search_input.send_keys(track_name)
        time.sleep(2)

        track_xpath = "//div[@data-testid='tracklist-row']//div[@role='row']"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, track_xpath)))
        track_rows = driver.find_elements(By.XPATH, track_xpath)

        if not track_rows:
            print("No track results found.")
            return "No tracks available."

        track_rows[0].click()
        print(f"Clicked on '{track_name}' result.")
        time.sleep(3)

        play_btn_xpath = "//button[@data-testid='control-button-play']"
        play_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, play_btn_xpath))
        )
        play_button.click()
        print("Playback started.")
        return f"Playing '{track_name}' on Spotify."

    except Exception as e:
        print(f"Spotify Error: {e}")
        return "Failed to play track on Spotify."

''' 
def play_in_spotify_app(track_name):
    open_app("spotify")  

    time.sleep(3)  
    pyautogui.hotkey('ctrl', 'l')  
    pyautogui.write(track_name)
    pyautogui.press('enter')

    time.sleep(2) 
    pyautogui.press('tab')  
    pyautogui.press('enter')  

    print(f"Attempting to play '{track_name}' in Spotify app")
'''
    
  
