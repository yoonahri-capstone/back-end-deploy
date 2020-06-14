from bs4 import BeautifulSoup
from selenium import webdriver
import tldextract
import time
import os

# URL = "https://www.instagram.com/p/B-lp4yghq5F/?utm_source=ig_web_copy_link"
# URL = "https://www.facebook.com/518619241508393/posts/2827717197265241/?sfnsn=mo"
# URL = "https://m.blog.naver.com/binhs9576/221788249228"
# URL = "https://www.youtube.com/watch?v=2dNc8ROMVlw"

global driver, URL, html, soup

def url_crawl(soup):
    save_list = []
    CURRENT_URL = driver.current_url
    extracted = tldextract.extract(URL)
    # print(extracted)
    extracted_current_url = tldextract.extract(CURRENT_URL)
    # print(extracted_current_url)
    domain = extracted.domain

    if domain == 'instagram':
        
        # driver.get("https://www.instagram.com/accounts/login/?hl=en")

        # id = ''
        # password = ''
        # id_input = driver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(2) > div > label > input')
        # id_input.send_keys(id)
        # password_input = driver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > div > label > input')
        # password_input.send_keys(password)
        # password_input.submit()

        # driver.find_element_by_name("username").send_keys(id)
        # driver.find_element_by_name("password").send_keys(password)
        # driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button').submit()
        # time.sleep(1)
        # element = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button')
        # driver.execute_script("arguments[0].click();", element)

        # driver.get(CURRENT_URL)
        # html = driver.page_source

        # soup = BeautifulSoup(html, 'lxml')
        try:
            if "비공개 계정입니다" in soup.find('h2', {"class": "rkEop"}):
                # print("비공개 계정입니다")
                return None
        except:
            pass

    if domain == 'naver' and extracted_current_url.subdomain == 'blog': #and extracted.suffix == 'me'
        driver.switch_to.frame('mainFrame')
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

    try:
        if domain == 'youtube' or domain=='youtu':
            title = soup.find("meta", {"property": "og:title"}).get("content")
        else:
            title = soup.head.title.text
            title = title.replace('\n', ' ')

        if domain == 'instagram':
            try:
                thumbnail = soup.select_one(".KL4Bh").img['src']
            except:
                thumbnail = soup.find("img", {"class": "_8jZFn"}).get("src")
        else:
            try:
                thumbnail = soup.find("meta", {"property": "og:image"}).get("content")
            except:
                thumbnail = None

        save_list.append(URL)
        save_list.append(title)
        save_list.append(thumbnail)
        save_list.append(extracted.domain)

    except Exception as e:
        print(e)
        return None

    return save_list


def youtube_hashtag():
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    all_hashtag = soup.find_all("a", {"class": "yt-simple-endpoint style-scope yt-formatted-string"})
    hashtag = [soup.find_all("a", {"class": "yt-simple-endpoint style-scope yt-formatted-string"})[n].string for n in range(0, len(all_hashtag))]
    # print(hashtag)
    driver.quit()
    return hashtag


def naver_hashtag():
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    all_hashtag = soup.find_all("span", {"class": "ell"})
    hashtag = [soup.find_all("span", {"class": "ell"})[n].string for n in range(0, len(all_hashtag))]
    # print(hashtag)
    if None in hashtag:
        hashtag = []
    driver.quit()
    return hashtag


def facebook_hashtag():
    hashtag = []
    try:
        all_hashtag = soup.find('div', "_1dwg _1w_m _q7o").find_all("span", {"class": "_58cm"})
        facebook_hashtag = [soup.find('div', "_1dwg _1w_m _q7o").find_all("span", {"class": "_58cm"})[n].string for n in range(0, len(all_hashtag))]

        for i in facebook_hashtag:
            hashtag.append('#' + i)
    except:
        pass
    
    driver.quit()
    return hashtag


def instagram_hashtag():
    check_comment = len(driver.find_elements_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div[2]/div[1]/ul/ul[1]/li/ul/li/div/button/span")) > 0
    if check_comment:
        driver.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/div[1]/article/div[2]/div[1]/ul/ul[1]/li/ul/li/div/button/span").click()
        time.sleep(0.5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        all_hashtag = soup.find_all("a", {"class": "xil3i"})
        hashtag = [soup.find_all("a", {"class": "xil3i"})[n].string for n in range(0, len(all_hashtag))]
    else:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        all_hashtag = soup.find_all("a", {"class": "xil3i"})
        hashtag = [soup.find_all("a", {"class": "xil3i"})[n].string for n in range(0, len(all_hashtag))]
    # print(hashtag)
    return hashtag


def hashtag_crawl():
    hashtags = []
    extracted = tldextract.extract(URL)
    if extracted.domain == 'youtube':
        hashtags = youtube_hashtag()
    elif extracted.domain == 'youtu':
        hashtags = youtube_hashtag()
    elif extracted.domain == 'naver':
        hashtags = naver_hashtag()
    elif extracted.domain == 'facebook':
        hashtags = facebook_hashtag()
    elif extracted.domain == 'instagram':
        hashtags = instagram_hashtag()
    hashtags = list(set(hashtags))  #중복제거
    hashtag_list = []
    for hashtag in hashtags:        #"#"없는 항목 제거
        if "#" in hashtag:
            hashtag_list.append(hashtag)
    return hashtag_list

    
def crawl_request(request):
    global driver, URL, html, soup

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument("lang=ko_KR")
    chrome_options.add_argument("disable-gpu")
    # chrome_options.add_argument("disable-infobars")
    # prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'plugins': 2, 'popups': 2,
    #                                                     'geolocation': 2, 'notifications': 2,
    #                                                     'auto_select_certificate': 2, 'fullscreen': 2, 'mouselock': 2,
    #                                                     'mixed_script': 2, 'media_stream': 2, 'media_stream_mic': 2,
    #                                                     'media_stream_camera': 2, 'protocol_handlers': 2,
    #                                                     'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
    #                                                     'push_messaging': 2, 'ssl_cert_decisions': 2,
    #                                                     'metro_switch_to_desktop': 2, 'protected_media_identifier': 2,
    #                                                     'app_banner': 2, 'site_engagement': 2, 'durable_storage': 2}}
    # chrome_options.add_experimental_option('prefs', prefs)
    # driver_path = os.path.abspath('memmem_app/chromedriver_windossw.exe')
    # driver_path = '/home/ubuntu/chromedriver.exe'

    # driver_path = driver_path.replace('\\', '/')
    # driver = webdriver.Chrome(executable_path = driver_path, options=chrome_options)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(20)

    # no error 가정
    URL = request

    if "instagram" in URL:
        driver.get("https://www.instagram.com/accounts/login/?hl=en")
        id = ''
        password = ''
        id_input = driver.find_element_by_css_selector(
            '#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(2) > div > label > input')
        id_input.send_keys(id)
        password_input = driver.find_element_by_css_selector(
            '#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > div > label > input')
        password_input.send_keys(password)
        password_input.submit()
        time.sleep(2)

    driver.get(URL)

    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

    except Exception as e:
        print(e)
    


    save_list = url_crawl(soup)
    hash_list = hashtag_crawl()

    if len(hash_list) > 0:
        return save_list + hash_list
    else:
        return save_list