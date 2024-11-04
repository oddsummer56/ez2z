import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import os
from ez2z.ids import get_song_id, get_album_id
from ez2z.artist import get_artist_details
from ez2z.album import get_album_details
from datetime import datetime
import insertDB

def get_song_details(song_id):
    lyrics_url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
    
    # User-Agent 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(lyrics_url, headers=headers)
    
    print(song_id)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 곡 제목
        song_div = soup.find('div', {'class': 'song_name'})
        song_title = song_div.get_text(strip=True).replace("곡명", "") if song_div else "Song title not found"
        print(f"Extracted song title : {song_title}")  # song_title을 출력

        # 발매일 추출
        release_tag = soup.select_one('div.meta dd:nth-of-type(2)') 
        s_release_year = release_tag.text.strip() if release_tag else "Release Year not found"
        
        # 문자열을 'YYYY-MM-DD' 형식으로 변환
        if s_release_year != "Release Year not found":
            release_date_obj = datetime.strptime(s_release_year, '%Y.%m.%d')
            s_release_date_str = release_date_obj.strftime('%Y-%m-%d')  # 'YYYY-MM-DD' 형식으로 변환
        else:
            s_release_date_str = None  # 발매일을 찾을 수 없는 경우 처리   

        # 가사 추출
        lyrics_div = soup.find('div', {'class': 'lyric'})
        lyrics = lyrics_div.get_text(separator="\n").strip() if lyrics_div else "Lyrics not found"
        
        # 노래 이미지 추출
        s_image_url_tag = soup.select_one('div.wrap_info div.thumb img') 
        s_image_url = s_image_url_tag.get('src') if s_image_url_tag else "Album Image not found"
        print(f"Extracted song image: {s_image_url}")  # song image url을 출력

        return song_title, s_release_date_str, lyrics, s_image_url

    else:
        return None, None, None, None  # 실패 시 None 반환

def save_song(song_id, song_title, s_release_date_str, lyrics, s_image_url):
    filename = "song.csv"
    
    # 기존 데이터 확인
    existing_song = set()
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_song.add(row['song_id'])
    
    # 중복 확인 후 csv 파일에 저장
    if song_id not in existing_song:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 파일이 존재하지 않으면 헤더 추가
            if os.path.getsize(filename) == 0:
                writer.writerow(['song_id', 'song_title', 's_release_date_str', 'lyrics', 's_image_url'])
            # 새로운 데이터 추가
            writer.writerow([song_id, song_title, s_release_date_str, lyrics, s_image_url])
            print(f"Added song ID {song_id} to the CSV file.")
    else:
        print(f"{song_id} 는 이미 존재하는 노래입니다.")

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    keyword = "pleasure shop"
    song_id = get_song_id(driver, keyword)  
    artist_name, artist_id = get_artist_details(song_id)
    album_id = get_album_id(driver, keyword)  
    album_title, a_image_url, a_release_date_str = get_album_details(album_id)
    
    if song_id:
        song_title, s_release_date_str, lyrics, s_image_url = get_song_details(song_id)
        
        if song_id and song_title:
            print(f"Data for {keyword}: {song_id} 노래")
    
            insertDB.insert_artist(artist_id, artist_name)
            insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
            insertDB.insert_song(song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url)
            save_song(song_id, song_title, s_release_date_str, lyrics, s_image_url)
        else:
            print("Error")
    else:
        print("Song ID not found.")
    
    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
