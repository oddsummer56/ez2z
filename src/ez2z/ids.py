from bs4 import BeautifulSoup
#from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Selenium WebDriver 설정
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음

def get_song_id(driver, keyword):
    base_url = "https://www.melon.com/search/song/index.htm"
    query = f"{keyword}"
    driver.get(f"{base_url}?q={query}")

    # 페이지가 로드되기까지 대기
    #time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 검색된 곡 정보의 리스트에서 첫 번째 곡의 ID를 가져옴
    song_info = soup.select_one('div.wrap.pd_none a')
    if song_info:
        # href에서 곡 ID 추출
        href_value = song_info['href']
        song_id = href_value.split('(')[1].split(')')[0].split(',')[-1].strip().replace("'", "")
        print(f"Extracted song ID: {song_id}")  # song_id를 출력
        return song_id
    else:
        return None



def get_album_id(driver, keyword):
    base_url = "https://www.melon.com/search/song/index.htm"
    query = f"{keyword}"
    driver.get(f"{base_url}?q={query}")

    # 페이지가 로드되기까지 대기
    #time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 앨범 ID 추출
     # 검색된 곡 정보의 리스트에서 첫 번째 곡의 ID를 가져옴
    album_info = soup.select_one('a[href*="goAlbumDetail"]')

    if album_info:
        # href에서 곡 ID 추출
        href_value = album_info['href']
        album_id = href_value.split("goAlbumDetail('")[1].split("')")[0]
        print(f"Extracted song ID: {album_id}")  # song_id를 출력
        return album_id
    else:
        return None