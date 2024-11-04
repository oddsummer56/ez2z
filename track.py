import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import os
from ids import get_song_id, get_album_id
from artist import get_artist_details
from album import get_album_details
from song import get_song_details
import insertDB

def get_track_list(album_id):
    album_url = f"https://www.melon.com/album/detail.htm?albumId={album_id}"

    # User-Agent 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(album_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 트랙 리스트 추출 시 HTML 확인을 위한 디버깅 출력
        print(f"Album URL: {album_url}")
        print("Raw HTML for debugging:\n", soup.prettify()[:1000])  # 출력 길이를 제한하여 첫 1000글자만 출력

        # 트랙 리스트 추출 (data-group-items가 'cd1'인 요소 선택)
        tracks = soup.select('tr[data-group-items="cd1"]')
        print(f"Found {len(tracks)} tracks")  # 트랙 수 출력

        if not tracks:
            print("No tracks found in the expected HTML structure.")
            return []

        track_list = []
        track_number = 1

        # 각 트랙 정보를 출력하여 태그가 올바르게 선택되었는지 확인
        for track in tracks:
            print(f"Track {track_number} raw HTML:\n", track.prettify())  # 각 트랙의 HTML 구조 출력
            
            # song_id 추출
            # <input> 태그의 value 속성에서 song_id 추출
            song_tag = track.select_one('input[name="input_check"]')
            if song_tag and song_tag.has_attr('value'):
                song_id = song_tag['value']
                print(f"Found song_id: {song_id}")
                track_list.append((track_number, song_id))
            else:
                print(f"Song ID not found for track {track_number}")
            
            track_number += 1

        return track_list
    else:
        print(f"Failed to retrieve track details for {album_id}. Status code: {response.status_code}")
        return []


def save_track(album_id, track_list):
    filename = "tracklist.csv"

    # 기존 데이터 확인
    existing_tracks = set()
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_tracks.add((row['album_id'], row['song_id'], row['track_num']))

    # 중복 확인 후 csv 파일에 저장
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 파일이 존재하지 않으면 헤더 추가
        if os.path.getsize(filename) == 0:
            writer.writerow(['album_id', 'song_id', 'track_num'])

        # 새로운 데이터 추가
        for track_number, song_id in track_list:
            if (album_id, song_id, track_number) not in existing_tracks:
                writer.writerow([album_id, song_id, track_number])
                print(f"Added track number {track_number}: song_id '{song_id}' to the CSV file.")
            else:
                print(f"Track number {track_number}: song_id '{song_id}' already exists in the CSV file.")

def main():
    # ChromeOptions 설정
    chrome_options = Options()
    #chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않고 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 키워드로 곡 ID 가져오기
        keyword = "bad love key"
        song_id = get_song_id(driver, keyword)  # driver를 인자로 전달
        artist_name, artist_id = get_artist_details(song_id)
        album_id = get_album_id(driver, keyword)  
        album_title, a_image_url, a_release_date_str = get_album_details(album_id)    
        song_title, s_release_date_str, lyrics, s_image_url = get_song_details(song_id)   

        if album_id:
            # 곡 ID로 트랙 리스트 가져오기
            track_list = get_track_list(album_id)
            
            # 트랙 리스트가 없으면 종료
            if not track_list:
                print(f"No tracks found for {album_title}.")
                return

            print("Track list found. Proceeding with the database insertion.")
            
            # 트랙 리스트가 있으면 데이터를 DB에 삽입
            insertDB.insert_artist(artist_id, artist_name)
            print("Inserted artist.")
            
            insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
            print("Inserted album.")
            
            insertDB.insert_song(song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url)
            print("Inserted song.")
            
            # 트랙 정보를 DB에 삽입
            for track_number, song_id in track_list:
                insertDB.insert_track(album_id, song_id, track_number)
                print(f"Inserted track {track_number} for song_id {song_id}.")
            
            # 트랙 리스트를 CSV 파일에 저장
            save_track(album_id, track_list)
            print(f"Saved track list to CSV for album: {album_title}")
        else:
            print("Album ID not found.")
    finally:
        driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
