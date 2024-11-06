import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
