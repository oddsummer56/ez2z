import requests
from bs4 import BeautifulSoup

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
    
        # 아티스트 이름 추출
        artist_div = soup.find('div', {'class': 'artist'})
        artist = artist_div.get_text(strip=True).replace("가수명", "") if artist_div else "Artist not found"
        
        return artist, artist_id

    else:
        return None, None  
