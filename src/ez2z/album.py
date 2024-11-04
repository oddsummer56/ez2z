import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import os
from ids import get_song_id, get_album_id
from artist import get_artist_details
from datetime import datetime
import insertDB

def get_album_details(album_id):
    lyrics_url = f"https://www.melon.com/album/detail.htm?albumId={album_id}"
    
    # User-Agent 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(lyrics_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 제목 추출
        title_tag = soup.select_one('div.song_name') 
        album_title = title_tag.get_text(strip=True).replace("앨범명", "") if title_tag else "앨범명을 찾을 수 없습니다."
        print(f"앨범명: {album_title}")  # album_title을 출력

        # 발매일 추출
        release_tag = soup.select_one('div.meta dd:nth-of-type(1)') 
        a_release_year = release_tag.text.strip() if release_tag else "발매일자를 찾을 수 없습니다."
        print(f"발매년도: {a_release_year}")  # release_year를 출력

        # 문자열을 'YYYY-MM-DD' 형식으로 변환
        if a_release_year != "변환하려는 발매일자를 찾을 수 없습니다.":
            release_date_obj = datetime.strptime(a_release_year, '%Y.%m.%d')
            a_release_date_str = release_date_obj.strftime('%Y-%m-%d')  # 'YYYY-MM-DD' 형식으로 변환
        else:
            a_release_date_str = None  # 발매일을 찾을 수 없는 경우 처리   

        print(f"발매년도 {a_release_year} 변환완료! ")  # release_year를 출력
 
        # 앨범 이미지 추출
        a_image_url_tag = soup.select_one('div.wrap_info div.thumb img') 
        a_image_url = a_image_url_tag.get('src') if a_image_url_tag else "앨범이미지를 찾을 수 없습니다."
        print(f"앨범이미지 추출완료!")  # album image url을 출력    

        return album_title, a_image_url, a_release_date_str

    else:
        return None, None, None  # 실패 시 None 반환

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    keyword = "옥탑방" ###################day6 finale 안됨#######################
    song_id = get_song_id(driver, keyword)
    album_id = get_album_id(driver, keyword)  
    artist_name, artist_id = get_artist_details(song_id)

    if album_id:
        album_title, a_image_url, a_release_date_str = get_album_details(album_id)
        
        if album_id and album_title:
            insertDB.insert_artist(artist_id, artist_name)
            insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
            print(f"{keyword}: {album_id} 앨범 INSERT 완료!")
        else:
            print("해당 앨범을 찾을 수 없습니다.")
    else:
        print("Album ID가 제대로 추출되지 않았습니다.")
    
    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
