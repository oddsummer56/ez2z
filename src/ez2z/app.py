from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from src.ez2z.track import get_track_list
from src.ez2z.ids import get_song_id, get_album_id
from src.ez2z.artist import get_artist_details
from src.ez2z.album import get_album_details
from src.ez2z.song import get_song_details
import src.ez2z.insertDB as insertDB

app = FastAPI()

# 요청 모델 정의
class SongRequest(BaseModel):
    keyword: str

@app.post("/add-song-data/")
def add_song_data(request: SongRequest):
    keyword = request.keyword

    # ChromeOptions 설정
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 키워드로 곡 ID 가져오기
        song_id = get_song_id(driver, keyword)
        if not song_id:
            raise HTTPException(status_code=404, detail="Song ID를 찾을 수 없습니다.")

        artist_name, artist_id = get_artist_details(song_id)
        album_id = get_album_id(driver, keyword)
        if not album_id:
            raise HTTPException(status_code=404, detail="Album ID를 찾을 수 없습니다.")

        album_title, a_image_url, a_release_date_str = get_album_details(album_id)
        song_title, s_release_date_str, lyrics, s_image_url = get_song_details(song_id)
        track_list = get_track_list(album_id)

        # 트랙리스트 및 DB 삽입 로직
        if insertDB.track_exists(album_id, song_id):
            return {"message": f"{album_title} 앨범트랙이 이미 존재합니다."}
        else:
            # 트랙 리스트가 없으면 데이터를 DB에 삽입
            insertDB.insert_artist(artist_id, artist_name)
            insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
            insertDB.insert_song(song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url)

            # 트랙 정보를 DB에 삽입 및 모든 track의 song 정보를 song 테이블에 삽입
            for track_number, track_song_id in track_list:
                insertDB.insert_track(album_id, track_song_id, track_number)
                
                # track_song_id로 song 정보 조회 및 song 테이블에 삽입
                if not insertDB.song_exists(track_song_id):  # song 테이블에 없으면 삽입
                    # 트랙 곡의 상세 정보 가져오기
                    track_song_title, track_release_date, track_lyrics, track_image_url = get_song_details(track_song_id)
                    insertDB.insert_song(track_song_id, track_song_title, album_id, artist_id, track_release_date, track_lyrics, track_image_url)

            return {"message": f"{song_title} / {album_title} 앨범의 모든 트랙이 성공적으로 DB에 저장되었습니다."}

    finally:
        driver.quit()
