import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import os
from ids import get_song_id, get_album_id
from artist import get_artist_details
from album import get_album_details
from datetime import datetime
import insertDB

def get_song_details(song_id):
    lyrics_url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
    
    # User-Agent 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(lyrics_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 곡 제목
        song_div = soup.find('div', {'class': 'song_name'})
        song_title = song_div.get_text(strip=True).replace("곡명", "") if song_div else "Song title not found"
        print(f"곡명: {song_title}")  # song_title을 출력

        # 발매일자 추출
        release_tag = soup.select_one('div.meta dd:nth-of-type(2)') 
        s_release_year = release_tag.text.strip() if release_tag else "Release Year not found"
        print(f"곡 발매일: {s_release_year}")  
        
        # 문자열을 'YYYY-MM-DD' 형식으로 변환
        if s_release_year != "Release Year not found":
            release_date_obj = datetime.strptime(s_release_year, '%Y.%m.%d')
            s_release_date_str = release_date_obj.strftime('%Y-%m-%d')  # 'YYYY-MM-DD' 형식으로 변환
        else:
            s_release_date_str = None  # 발매일을 찾을 수 없는 경우 처리   
        print(f"곡 발매일 {s_release_year} 변환완료! ")  
        
        # 가사 추출
        lyrics_div = soup.find('div', {'class': 'lyric'})
        lyrics = lyrics_div.get_text(separator="\n").strip() if lyrics_div else "Lyrics not found"
        
        # 노래 이미지 추출
        s_image_url_tag = soup.select_one('div.wrap_info div.thumb img') 
        s_image_url = s_image_url_tag.get('src') if s_image_url_tag else "Album Image not found"
        print(f"노래이미지 추출완료!")  # song image url을 출력
        print(f"===================")
        return song_title, s_release_date_str, lyrics, s_image_url

    else:
        return None, None, None, None  # 실패 시 None 반환

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    keyword = "즐거운"
    song_id = get_song_id(driver, keyword)  
    artist_name, artist_id = get_artist_details(song_id)
    album_id = get_album_id(driver, keyword)  
    album_title, a_image_url, a_release_date_str = get_album_details(album_id)
    song_title, s_release_date_str, lyrics, s_image_url = get_song_details(song_id)
    
    if song_id:
        # DB에 해당 노래가 있는지 확인
        if insertDB.song_exists(song_id): #songID가 있으면 DB INSERT를 종료 (정보 받아오는걸로 변경?###########################)
            print(f"노래 {song_title} 가 이미 존재합니다.")
        else:
            if song_id and song_title:
                print(f"{keyword}({song_id}) 노래 INSERT 완료!")
                    
                insertDB.insert_artist(artist_id, artist_name)
                insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
                insertDB.insert_song(song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url)
            else:
                print("Error")
    else:
        print("Song ID가 제대로 추출되지 않았습니다.")
    
    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
