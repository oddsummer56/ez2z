import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
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
    
        # 아티스트 이름 추출
        artist_div = soup.find('div', {'class': 'artist'})
        artist = artist_div.get_text(strip=True).replace("가수명", "") if artist_div else "Artist not found"
        
        return artist, artist_id

    else:
        return None, None  

def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    from song import get_song_details

    keyword = "bad love key"
    song_id = get_song_id(driver, keyword)  
    artist, artist_id = get_artist_details(song_id)
    song_title, _, _, _ = get_song_details(song_id)
    
    if artist_id: 
        # DB에 해당 아티스트가 있는지 확인
        if insertDB.artist_exists(artist_id): #artistID가 있으면 DB INSERT를 종료 (정보 받아오는걸로 변경?###########################)
            print(f"노래 {song_title}의 artist {artist}가 이미 존재합니다.")
        else:
            if artist and artist_id:
                insertDB.insert_artist(artist_id, artist)
                print(f"노래 {song_title}의 artist {artist} INSERT 완료!")
            else:
                print("Artist details not found.")
    else:
        print("Artist not found.")
    
    print(f"Extracted artist ID: {artist_id}") 
    print(f"Extracted artist : {artist}")  

    driver.quit()  # WebDriver 종료

if __name__ == "__main__":
    main()
