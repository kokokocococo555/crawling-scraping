#!usr/bin/python
# -*- coding: UTF-8 -*-

## 1. 準備

### 1.1. モジュールのインポート
import os
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

### 1.2. logのためのおまじない
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

## 2. 関数の定義

### 2.1. 作品名を取得
def getStoryTitle(url):
    html = urlopen(url)
    bsObj = BeautifulSoup(html,"html.parser")

    # 本文のHTMLをリスト形式で抜き出す
    story_title = bsObj.findAll("p",{"class":"novel_title"})[0].get_text()

    return story_title

### 2.2. 本文ページから本文を抜き出す
# （getAllTexts関数内で使用）
def getMainText(title, date, url):
    html = urlopen(url)
    bsObj = BeautifulSoup(html,"html.parser")

    # 本文のHTMLをリスト形式で抜き出す
    text_htmls = bsObj.findAll("div",{"id":"novel_honbun"})[0].findAll("p")

    # 「title<title_date>date<date_url>url<url_text>text」という様式でテキスト化
    text = title + "<title_date>" + date + "<date_url>" + url + "<url_text>"
    for text_html in text_htmls:
        text = text + text_html.get_text() + "\n"

    # サーバに負荷をかけないために、1s処理を止める
    time.sleep(1)

    return text

### 2.3. すべての本文ページに順次アクセスし、本文を抜き出してリスト化
def getAllTexts(url):
    start = time.time() # 所要時間の計測スタート

    # 作品ページから各話の情報を抜き出す
    html = urlopen(url)
    bsObj = BeautifulSoup(html,"html.parser")

    text_url_lists =[]

    for i in range(len(bsObj.findAll("dd",{"class":"subtitle"}))):
        title = bsObj.findAll("dd",{"class":"subtitle"})[i].findAll("a")[0].get_text()
        date = bsObj.findAll("dt",{"class":"long_update"})[i].get_text()
        url_2 = bsObj.findAll("dd",{"class":"subtitle"})[i].findAll("a")[0].attrs["href"]
        tmp_list = [title, date, url_2]
        text_url_lists.append(tmp_list)


    # 各話それぞれで処理を行い、「title<title_date>date<date_text>text」という様式で各話をリスト化
    text_list = []
    for text_url_list in text_url_lists:
        title = text_url_list[0]
        date = text_url_list[1]
        url_no = text_url_list[2]
        url_no = url_no.split("/")[-2]
        full_url = url + url_no

        html = urlopen(full_url)
        bsObj = BeautifulSoup(html,"html.parser")

        # 「title<title_date>date<date_url>url<url_text>text」という様式でテキスト化
        text = getMainText(title, date, full_url)

        # リストに追加
        text_list.append(text)

        # 処理状況の出力
        elapsed_time = time.time() - start
        logger.debug("{0} (scraping_elapsed_time:{1})".format(full_url, elapsed_time)) # 所要時間を順次表示

    # 処理状況の出力
    elapsed_time = time.time() - start
    logger.debug("scraping_FINISH!! {0} (elapsed_time:{1})".format(url, elapsed_time)) # 合計所要時間を表示

    return text_list

### 2.4. txtファイルに保存
# （textSave関数内で使用）
def fileSave(title, number, text, directory_name, encoding="utf-8"):
    number_padded = number.zfill(4) # 話数的な数字をゼロパディングで作成
    fileName = title.replace("/", "-") + ".txt"
    filePath = directory_name + "/[" + number_padded + "]_" + fileName
    with open(filePath, "w", encoding=encoding) as f:
        f.write(text)

### 2.5. すべての話を別個に.txtファイル化
def textSave(text_list, directory_name):
    for text_data in text_list:
        title = text_data.split("<title_date>")[0]
        number = text_data.split("<url_text>")[0].split("/")[-1] # 話数的な数字を取得
        fileSave(title, number, text_data, directory_name, encoding="utf-8")

### 2.5.(b) すべての話を別個に.txtファイル化（テキストのみ保存するバージョン）
# def textSave(text_list, directory_name):
#     for text_data in text_list:
#         title = text_data.split("<title_date>")[0]
#         text = text_data.split("<url_text>")[1]
#         number = text_data.split("<url_text>")[0].split("/")[-1] # 話数的な数字を取得
#         fileSave(title, number, text, directory_name, encoding="utf-8")

## 3. スクレイピングを実行

# メイン処理
# --------------------------------------
# 作品ページのURLを指定（コメントアウト・コメントインで指定できるようにしています）
# ※すでに保存済みの作品を指定するとエラーが出て処理が止まります。
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

# --------------------------------------
# 各作品を保存するディレクトリ名を指定（存在しなければ作成されます）
directory = "text"
# --------------------------------------

# 各作品に処理を実行
for url in url_list:
    # 作品名を取得
    story_title = getStoryTitle(url)

    # 作品名をディレクトリ名にする
    directory_name = directory + "/" + story_title

    # 作品ディレクトリを作成
    os.makedirs(directory_name)

    # すべての本文ページから本文を抜き出してリスト化
    text_list = getAllTexts(url)

    # 各話を別々に.txtファイルで保存
    textSave(text_list, directory_name)
