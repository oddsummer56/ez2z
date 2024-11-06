import requests
from bs4 import BeautifulSoup
from datetime import datetime


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

