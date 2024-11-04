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
    
    print(album_id)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 제목 추출
        title_tag = soup.select_one('div.song_name') 
        album_title = title_tag.get_text(strip=True).replace("앨범명", "") if title_tag else "Album title not found"
        print(f"Album title: {album_title}")  # album_title을 출력

        # 앨범 이미지 추출
        a_image_url_tag = soup.select_one('div.wrap_info div.thumb img') 
        a_image_url = a_image_url_tag.get('src') if a_image_url_tag else "Album Image not found"
        print(f"Extracted album image: {a_image_url}")  # album image url을 출력

        # 발매일 추출
        release_tag = soup.select_one('div.meta dd:nth-of-type(1)') 
        a_release_year = release_tag.text.strip() if release_tag else "Release Year not found"
        print(f"Extracted release year: {a_release_year}")  # release_year를 출력

        # 문자열을 'YYYY-MM-DD' 형식으로 변환
        if a_release_year != "Release Year not found":
            release_date_obj = datetime.strptime(a_release_year, '%Y.%m.%d')
            a_release_date_str = release_date_obj.strftime('%Y-%m-%d')  # 'YYYY-MM-DD' 형식으로 변환
        else:
            a_release_date_str = None  # 발매일을 찾을 수 없는 경우 처리   

        print(f"Extracted release year: {a_release_year}")  # release_year를 출력
        
        return album_title, a_image_url, a_release_date_str
    
    else:
        return None, None, None  # 실패 시 None 반환

def save_album(album_id, album_title, a_image_url, a_release_date_str):
    filename = "album.csv"
    
    # 기존 데이터 확인
    existing_album = set()
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_album.add(row['album_id'])
    
    # 중복 확인 후 csv 파일에 저장
    if album_id not in existing_album:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 파일이 존재하지 않으면 헤더 추가
            if os.path.getsize(filename) == 0:
                writer.writerow(['album_id', 'album_title', 'album_image', 's_release_date_str'])
            # 새로운 데이터 추가
            writer.writerow([album_id, album_title, a_image_url, a_release_date_str])
            print(f"Added album ID {album_id} to the CSV file.")
    else:
        print(f"{album_id} 는 이미 존재하는 앨범입니다.")

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    keyword = "happy"
    song_id = get_song_id(driver, keyword)
    artist_name, artist_id = get_artist_details(song_id)
    album_id = get_album_id(driver, keyword)  # driver를 인자로 전달

    if album_id:
        album_title, a_image_url, a_release_date_str = get_album_details(album_id)
        
        if album_id and album_title:
            print(f"Data for {keyword}: {album_id} 앨범")
            save_album(album_id, album_title, a_image_url, a_release_date_str)
            insertDB.insert_artist(artist_id, artist_name)
            insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
        else:
            print("Artist details not found.")
    else:
        print("Album ID not found.")
    
    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
