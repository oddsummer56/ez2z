import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
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

        # 앨범명 추출
        title_tag = soup.select_one('div.song_name') 
        album_title = title_tag.get_text(strip=True).replace("앨범명", "") if title_tag else "앨범명을 찾을 수 없습니다."
        print(f"앨범명: {album_title}")  

        # 발매일 추출
        release_tag = soup.select_one('div.meta dd:nth-of-type(1)') 
        a_release_year = release_tag.text.strip() if release_tag else "발매일자를 찾을 수 없습니다."
        print(f"앨범 발매일: {a_release_year}")  

        # 문자열을 'YYYY-MM-DD' 형식으로 변환
        if a_release_year != "변환하려는 발매일자를 찾을 수 없습니다.":
            release_date_obj = datetime.strptime(a_release_year, '%Y.%m.%d')
            a_release_date_str = release_date_obj.strftime('%Y-%m-%d')  # 'YYYY-MM-DD' 형식으로 변환
        else:
            a_release_date_str = None  # 발매일을 찾을 수 없는 경우 처리   

        print(f"앨범 발매일 {a_release_year} 변환완료! ")  

        # 앨범 이미지 추출
        a_image_url_tag = soup.select_one('div.wrap_info div.thumb img') 
        a_image_url = a_image_url_tag.get('src') if a_image_url_tag else "앨범이미지를 찾을 수 없습니다."
        print(f"앨범이미지 추출완료!") 
        print(f"===================")

        return album_title, a_image_url, a_release_date_str

    else:
        return None, None, None  # 실패 시 None 반환

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    keyword = "히치하이킹" 
    song_id = get_song_id(driver, keyword)
    album_id = get_album_id(driver, keyword)  
    artist_name, artist_id = get_artist_details(song_id)

    album_title, a_image_url, a_release_date_str = get_album_details(album_id)

    if album_id:
        # DB에 해당 앨범이 있는지 확인
        if insertDB.album_exists(album_id):  # albumID가 있으면 DB INSERT를 종료 (정보 받아오는걸로 변경?###########################)
            print(f"{keyword}({album_id}) 앨범이 이미 존재합니다! DB INSERT를 종료합니다.")
        else:
            if album_title:
                insertDB.insert_artist(artist_id, artist_name)
                insertDB.insert_album(album_id, album_title, artist_id, a_release_date_str, a_image_url)
                print(f"{keyword}({album_id}) 앨범 INSERT 완료!")
            else:
                print("해당 앨범을 찾을 수 없습니다.")
    else:
        print("Album ID가 제대로 추출되지 않았습니다.")
    
    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
