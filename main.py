import re
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup

def get_tables(url, page):
    response = requests.get(f"{url}0/{page}/")
    # lxmlはパーサー
    soup = BeautifulSoup(response.text, 'lxml')
    # ページ内の全テーブルを取得
    tables = soup.find_all('table')
    return tables




def get_song_list(url):

    # 保存するDataFrameのカラム名
    columns_names = ['曲名', '歌手名', '作詞者名', '作曲者名', '歌い出し', '歌詞URL']

    all_song_list = []
    page_no = 0

    # ページ毎のループ
    while True:
        page_no += 1
        # ページ単位でのテーブルを取得する。
        tables = get_tables(url, page_no)

        # テーブルが取得できない場合は終了
        if len(tables) == 0:
            break

        # 1秒間スリープ（負荷対策）
        time.sleep(1)

        # テーブル毎のループ
        for table in tables:
            for row in table.find_all('tr', class_='border-bottom'):
                row_data = []

                # ヘッダー以外の行の場合に処理を実行する。
                if row.find('td') is not None:

                    # 「曲名」〜「歌い出し」までのカラムを追加
                    song_name = row.find_all('span')[0].text
                    artist = row.find_all('td')[1].text
                    lyricist = row.find_all('td')[2].text
                    composer = row.find_all('td')[3].text
                    start_singing = row.find_all('span')[3].text
                    song_url = row.find('a', class_='py-2 py-lg-0').get('href')

                    # 行を追加
                    row_data.append(song_name)
                    row_data.append(artist)
                    row_data.append(lyricist)
                    row_data.append(composer)
                    row_data.append(start_singing)
                    row_data.append(song_url)

                    all_song_list.append(row_data)

    # データフレームに格納して返す
    lyrics_df = pd.DataFrame(all_song_list, columns=columns_names)

    return lyrics_df

lylics_url = "https://www.uta-net.com/artist/22653/"
lyrics_df = get_song_list(lylics_url)

def get_lyrics(lyrics_url, url_count, comp_count=[0]):
    comp_count[0] += 1
    print(str(comp_count[0]) + '/' + str(url_count) + '曲 歌詞URL：' + lyrics_url)

    # 歌詞URL
    url = f"https://www.uta-net.com{lyrics_url}"
    # 歌詞取得
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    song_lyrics = soup.find('div', id='kashi_area')
    lyrics = song_lyrics.text
    # 1秒間スリープ（負荷対策）
    time.sleep(1)
    return lyrics

lyrics_df["歌詞"] = lyrics_df["歌詞URL"].apply(get_lyrics, url_count = len(lyrics_df))
lyrics_df.to_csv('scraped.csv')
print('スクレイピング 完了')