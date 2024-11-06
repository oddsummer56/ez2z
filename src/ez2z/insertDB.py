import pymysql

# 공통 데이터베이스 연결 함수
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='oddsummer56',
        database='OurLyricsDB',
        port=3306,
        charset='utf8mb4',
        #auth_plugin='mysql_native_password',
        cursorclass=pymysql.cursors.DictCursor
    )

def album_exists(album_id):
    # albumID가 데이터베이스에 있는지 체크
    connection = get_db_connection()
    with connection.cursor() as cursor:
        query = "SELECT 1 FROM album WHERE albumID = %s"
        cursor.execute(query, (album_id,))
        result = cursor.fetchone()  
        return result is not None
    
def song_exists(song_id):
    # songID가 데이터베이스에 있는지 체크
    connection = get_db_connection()
    with connection.cursor() as cursor:
        query = "SELECT 1 FROM song WHERE songID = %s"
        cursor.execute(query, (song_id,))
        result = cursor.fetchone()  
        return result is not None
    
def artist_exists(artist_id):
    # artistID가 데이터베이스에 있는지 체크
    connection = get_db_connection()
    with connection.cursor() as cursor:
        query = "SELECT 1 FROM artist WHERE artistID = %s"
        cursor.execute(query, (artist_id,))
        result = cursor.fetchone()  
        return result is not None
    
def track_exists(album_id, song_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        query = "SELECT 1 FROM tracklist WHERE albumID = %s AND songID = %s"
        cursor.execute(query, (album_id, song_id))
        result = cursor.fetchone()  
        return result is not None

# 아티스트와 곡 데이터를 삽입하는 함수
def insert_artist(artist_id, artist):
    # 데이터베이스 연결
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:

            insert_artist_sql = '''
            INSERT IGNORE INTO artist (artistID, artist) VALUES (%s, %s)
            '''
            cursor.execute(insert_artist_sql, (artist_id, artist))
        
        # 커밋하여 데이터베이스에 반영
        connection.commit()

    finally:
        # 연결 종료
        connection.close()

# 앨범 데이터를 삽입하는 함수
def insert_album(album_id, album_title, artist_id, a_image_url, a_release_date_str):
    # 데이터베이스 연결
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            # artist 테이블에 해당 artistID가 있는지 확인
            select_artist_sql = "SELECT artistID FROM artist WHERE artistID = %s"
            cursor.execute(select_artist_sql, (artist_id))
            artist_exists = cursor.fetchone()

            # 아티스트가 존재하지 않는 경우 앨범을 삽입하지 않음
            if not artist_exists:
                print(f"Artist ID {artist_id} does not exist. Album {album_title} cannot be added.")
                return

            # 앨범 정보 삽입문 (이미 존재하는 경우 무시)
            insert_album_sql = '''
            INSERT IGNORE INTO album (albumID, albumTitle, artistID, releaseDate, albumImage) VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_album_sql, (album_id, album_title, artist_id,  a_image_url, a_release_date_str))
        
        # 커밋하여 데이터베이스에 반영
        connection.commit()

    finally:
        # 연결 종료
        connection.close()

# 곡 데이터를 삽입하는 함수
def insert_song(song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url):
    # 데이터베이스 연결
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            # 앨범 및 아티스트가 데이터베이스에 존재하는지 확인
            select_album_sql = "SELECT albumID FROM album WHERE albumID = %s"
            cursor.execute(select_album_sql, (album_id,))
            album_exists = cursor.fetchone()

            select_artist_sql = "SELECT artistID FROM artist WHERE artistID = %s"
            cursor.execute(select_artist_sql, (artist_id,))
            artist_exists = cursor.fetchone()

            # 앨범 또는 아티스트가 존재하지 않는 경우 곡을 삽입하지 않음
            if not album_exists or not artist_exists:
                print(f"Either album ID {album_id} or artist ID {artist_id} does not exist. Song {song_title} cannot be added.")
                return

            # 곡 정보 삽입문 (이미 존재하는 경우 무시)
            insert_song_sql = '''
            INSERT IGNORE INTO song (songID, songTitle, albumID, artistID, releaseDate, lyrics, songImage) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_song_sql, (song_id, song_title, album_id, artist_id, s_release_date_str, lyrics, s_image_url))
        
        # 커밋하여 데이터베이스에 반영
        connection.commit()

    finally:
        # 연결 종료
        connection.close()

def insert_track(album_id, song_id, track_number):
    connection = get_db_connection()
    
    try: 
        with connection.cursor() as cursor: 
            # SQL INSERT 쿼리 수행
            sql = """
            INSERT INTO tracklist (albumID, songID, trackNum)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (album_id, song_id, track_number))
            connection.commit()
    except Exception as e:
        print(f"트랙 INSERT에 실패하였습니다 {track_number}: {e}")
    finally:
        connection.close()

