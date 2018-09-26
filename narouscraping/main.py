#!usr/bin/python
# -*- coding: UTF-8 -*-

# 0. logのためのおまじない
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

# 1. モジュールのインポート
import os
import time
import datetime
import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup

# 2. メイン処理
def main():
    """
    メイン処理
    """
    # --------------------------------------
    # 作品ページのURLを指定（コメントアウト・コメントインで指定できるようにしています）
    url_list = [
        "https://ncode.syosetu.com/n2267be/" # Ｒｅ：ゼロから始める異世界生活
        ,
        "https://ncode.syosetu.com/n6316bn/" # 転生したらスライムだった件
    #     ,
    #     "https://ncode.syosetu.com/n2031cu/" # 異世界転移で女神様から祝福を！　～いえ、手持ちの異能があるので結構です～
    #     ,
    #     "https://ncode.syosetu.com/n3009bk/" # 盾の勇者の成り上がり
    #     ,
    #     "https://ncode.syosetu.com/n6475db/" # 私、能力は平均値でって言ったよね！
    #     ,
    #     "https://ncode.syosetu.com/n5881cl/" # 賢者の孫
               ]
    # --------------------------------------
    # 各作品について処理
    for url in url_list:
        stories = []
        bs_obj = make_bs_obj(url)
        time.sleep(3)

        url_list = ["https://ncode.syosetu.com" + a_bs_obj.find("a").attrs["href"] for a_bs_obj in bs_obj.findAll("dl", {"class": "novel_sublist2"})]
        date_list = bs_obj.findAll("dt",{"class":"long_update"})
        novel_title = bs_obj.find("p",{"class":"novel_title"}).get_text()
        for s in r'\/*?"<>:|':
            novel_title = novel_title.replace(s, '')

        # 各話の本文情報を取得
        for j in range(len(url_list)):
            bs_obj = make_bs_obj(url_list[j])
            time.sleep(3)

            stories.append({
                "No": j+1,
                "title": bs_obj.find("p", {"class": "novel_subtitle"}).get_text(),
                "url": url,
                "date": date_list[j].get_text(),
                "text": get_main_text(bs_obj),
                })

        save_as_csv(stories, novel_title)
  
# 3. BeautifulSoupObjectを作成
def make_bs_obj(url):
    """
    BeautifulSoupObjectを作成
    """
    html = urlopen(url)
    logger.debug('access {} ...'.format(url))

    return BeautifulSoup(html,"html.parser")

# 4. 各話のコンテンツをスクレイピング
def get_main_text(bs_obj):
    """
    各話のコンテンツをスクレイピング
    """
    text = ""
    text_htmls = bs_obj.findAll("div",{"id":"novel_honbun"})[0].findAll("p")

    for text_html in text_htmls:
        text = text + text_html.get_text() + "\n\n"

    return text

# 5. csvファイルに保存
def save_as_csv(stories, novel_title = ""):
    """
    csvファイルにデータを保存
    """
    # バックアップファイルの保存先の指定    
    directory_name = "novels"
    # ディレクトリが存在しなければ作成する
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    # ファイル名の作成
    today = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm')
    csv_name = os.path.join(directory_name, 'narou_ranking「{}」[{}].csv'.format(novel_title, today))

    # 列名（1行目）を作成
    col_name = ['No', 'title', 'url', 'date', 'text']

    with open(csv_name, 'w', newline='', encoding='utf-8') as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerow(col_name) # 列名を記入

        # csvに1行ずつ書き込み
        for story in stories:
            row_items = [story['No'], story['title'], story['url'], story['date'], story['text']]
            csv_writer.writerow(row_items)

    print(csv_name, ' saved...')
   
if __name__ == '__main__':
    main()
