import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.ez2z.ids import get_song_id, get_album_id
from src.ez2z.artist import get_artist_details
from src.ez2z.album import get_album_details
from src.ez2z.song import get_song_details
from src.ez2z import insertDB

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
        # print(f"Album URL: {album_url}")

        # 트랙 리스트 추출 (data-group-items가 'cd1'인 요소 선택)
        tracks = soup.select('tr[data-group-items="cd1"]')
        print(f"{len(tracks)}개의 트랙을 찾았습니다.")  # 트랙 수 출력

        if not tracks:
            print("트랙을 찾지 못했습니다.")
            return []

        track_list = []
        track_number = 1

        # 각 트랙 정보를 출력하여 태그가 올바르게 선택되었는지 확인
        for track in tracks:            
            # <input> 태그의 value 속성에서 song_id 추출
            song_tag = track.select_one('input[name="input_check"]')
            if song_tag and song_tag.has_attr('value'):
                song_id = song_tag['value']
                # print(f"Found song_id: {song_id}")
                track_list.append((track_number, song_id))
            else:
                print(f"{song_id}에 해당되는 trackNum을 찾지 못했습니다.")
            
            track_number += 1

        return track_list
    else:
        print(f"{album_id} 앨범의 트랙정보를 찾을 수 없습니다. Status code: {response.status_code}")
        return []

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
        keyword = "어른아이 세븐틴"
        song_id = get_song_id(driver, keyword)  # driver를 인자로 전달
        artist_name, artist_id = get_artist_details(song_id)
        album_id = get_album_id(driver, keyword)  
        album_title, a_image_url, a_release_date_str = get_album_details(album_id)    
        song_title, s_release_date_str, lyrics, s_image_url = get_song_details(song_id)   
        track_list = get_track_list(album_id) # 곡 ID로 트랙 리스트 가져오기


        if album_id:
            # DB에 해당 트랙리스트가 들어있는지 확인
            if insertDB.track_exists(album_id, song_id): #해당되는 트랙리스트가 있으면 DB INSERT를 종료 (정보 받아오는걸로 변경?###########################)
                print(f"{album_title} 앨범트랙이 이미 존재합니다.")
            else:
                if track_list:            
                    # 트랙 리스트가 없으면 데이터를 DB에 삽입
                    insertDB.insert_artist(artist_id, artist_name)
                    print("아티스트 Insert 완료.")
                    
                    insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
                    print("앨범 Insert 완료.")
                    
                    insertDB.insert_song(song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url)
                    print("노래 Insert 완료.")
                else:
                    print("해당 트랙리스트를 찾을 수 없습니다.")
                
                # 트랙 정보를 DB에 삽입
                for track_number, song_id in track_list:
                    insertDB.insert_track(album_id, song_id, track_number)
                    print(f"{album_title}의 {track_number}번 트랙 {song_id} Insert 완료.")
                        # track_song_id로 song 정보 조회 및 song 테이블에 삽입
                    
                    if not insertDB.song_exists(song_id):  # song 테이블에 없으면 삽입
                        # 트랙 곡의 상세 정보 가져오기
                        track_song_title, track_release_date, track_lyrics, track_image_url = get_song_details(song_id)
                        insertDB.insert_song(song_id, track_song_title, album_id, artist_id, track_release_date, track_lyrics, track_image_url)
                        print(f"트랙 노래 {track_song_title} Insert 완료.")
        else:
            print("Album ID가 제대로 추출되지 않았습니다.")
    finally:
        driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
