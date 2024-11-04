import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import os
from ids import get_song_id
import insertDB

def get_artist_details(song_id):
    lyrics_url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
    
    # User-Agent 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(lyrics_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 아티스트 ID 추출
        artist_tag = soup.select_one('div.artist a[href*="goArtistDetail"]')
        artist_id = artist_tag['href'].split('(')[1].split(')')[0].replace("'", "") if artist_tag else "Artist ID not found"
        print(f"Extracted artist ID: {artist_id}")  # artist_id를 출력

        # 아티스트 이름 추출
        artist_div = soup.find('div', {'class': 'artist'})
        artist = artist_div.get_text(strip=True).replace("가수명", "") if artist_div else "Artist not found"
        print(f"Extracted artist : {artist}")  # artist 이름을 출력
        
        return artist, artist_id

    else:
        return None, None  # 실패 시 None 반환

def save_artist(artist, artist_id):
    filename = "artist.csv"
    
    # 기존 데이터 확인
    existing_artist = set()
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_artist.add(row['artist_id'])
    
    # 중복 확인 후 csv 파일에 저장
    if artist_id not in existing_artist:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 파일이 존재하지 않으면 헤더 추가
            if os.path.getsize(filename) == 0:
                writer.writerow(['artist', 'artist_id'])
            # 새로운 데이터 추가
            writer.writerow([artist, artist_id])
            print(f"Added artist {artist} to the CSV file.")
            print(f"Added artist ID {artist_id} to the CSV file.")
    else:
        print(f"{artist} 는 이미 존재하는 아티스트 입니다.")

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    keyword = "bad love"
    song_id = get_song_id(driver, keyword)  # driver를 인자로 전달
    if song_id:
        artist, artist_id = get_artist_details(song_id)
        if artist and artist_id:
            print(f"Data for {keyword}: {artist}, {artist_id}")

            save_artist(artist, artist_id)
            #insertDB.insert_artist(artist_id, artist)
        else:
            print("Artist details not found.")
    else:
        print("Song ID not found.")
    
    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
