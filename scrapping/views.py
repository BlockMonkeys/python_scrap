from django.shortcuts import render
from django.template import loader
from django.template import RequestContext

# Create your views here.
from django.http import HttpResponse
from bs4 import BeautifulSoup as bs
import certifi
import urllib3
from selenium import webdriver
from urllib.parse import quote
from time import sleep
import time
import csv
import io
import urllib, base64
import datetime
import pandas as pd
from konlpy.tag import Mecab
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
mecab = Mecab()

# 스코프 문제해결을 위한 전역변수 선언
page_index_urls = []
blog_urls = []
blog_contents = []
dict_blogDatas = {}
userReqKeyword = ""
nlpResult = []


#Home (1. 크롤링-스크래핑-CSV추출) + (2. Konlpy-WordCloud-Pandas)
def index(request):
    data = {
        "msg": "아래 입력창에 필요한 정보를 입력하면 크롤링을 시작합니다."
    }
    #render(request, "HTML파일경로 /template상태임", 전달할 데이터)
    return render(request, 'scrapping/index.html', data)

#크롤링 URL 검색결과 탐색 -> 블로그 URL 가져오기
def crawPage(request):
    #초기화
    page_index_urls = []

    # 메인 페이지에서 POST로 받아온, 유저의 인풋 값
    userReqMaxPageNumber = int(request.POST.get("maxPageNum"))
    userReqKeyword = request.POST.get("keyword")

    # Base URL 설정 (default: Naver Cafe 검색)
    baseURL = "https://section.blog.naver.com/Search/Post.naver"

    #셀레니움 경로설정 후, URL 탐색 (경로는 절대경로만 받는다)
    driver = webdriver.Chrome("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/chromedriver")
    driver.implicitly_wait(3)

    #사용자가 요청한 내용대로, pageNumber를 매개변수로잡고
    for page_index in range(userReqMaxPageNumber):
        page_url = baseURL
        page_url += ("?pageNo=" + str(page_index+1))
        page_url += "&rangeType=ALL&orderBy=sim&"
        page_url += "keyword=" + quote(userReqKeyword)
        driver.get(page_url)
        page_index_urls.append(page_url)
        time.sleep(3)

    #드라이버가 다 돌고나면 클로즈 시킴.
    driver.close()

    #블로그 URL 가져오기
    for blogs in page_index_urls:
        driver = webdriver.Chrome("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/chromedriver")
        driver.implicitly_wait(3)
        driver.get(blogs)
        time.sleep(5)

        page = driver.page_source
        driver.close()

    soup = bs(page, "html.parser")
    time.sleep(3)

    blog_a_tags = soup.select("div.list_search_post a.desc_inner")
    for tag in blog_a_tags:
        blog_urls.append(tag['href'])

    data = {
        "msg": "아래 입력창에 필요한 정보를 입력하면 크롤링을 시작합니다.",
        "maxPageNum": request.POST.get("maxPageNum"),
        "keyword": request.POST.get("keyword"),
        "urls": page_index_urls,
        "blogURLs": blog_urls,
    }
    return render(request, 'scrapping/showURLs.html', data)

#크롤링한 블로그 URL들을 Scrapping해서 필요한 데이터를 추출 (I-frame 주의!)
def scrapPage(request):
    for blog_url in blog_urls:
        driver = webdriver.Chrome("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/chromedriver")
        driver.implicitly_wait(3)

        driver.get(blog_url)
        time.sleep(5)

        page = driver.page_source

        driver.switch_to.frame("mainFrame")
        inner_page = driver.page_source
        soup = bs(inner_page, "html.parser")
        contents = soup.select("p > span")

        blog_content = ' '.join([content.text.strip() for content in contents])
        blog_contents.append(blog_content)

        driver.close()

    #추출한 블로그의 데이터를 딕셔너리 형태로 Key:Value로 정리할 것.
    for idx, blogs in enumerate(zip(blog_urls, blog_contents)):
        dict_blogDatas[idx] = {
            "url": blogs[0],
            "content": blogs[1],
        }

    # 파일다운로드 자동으로 해야함.
    myFilePathforCrawling = "./csv/crawData.csv"
    with open(myFilePathforCrawling, "w", newline="") as csvfile:
        dataWriter = csv.writer(csvfile, delimiter=",")
        for key, val in dict_blogDatas.items():
            dataWriter.writerow([key, dict_blogDatas[key]['url'], dict_blogDatas[key]['content']])

    data = {
        "blogContent": dict_blogDatas
    }

    return render(request, 'scrapping/scrap.html', data)

#크롤링 데이터는 자동이지만, CSV파일을 추출하고 싶을 경우 사용할 버튼용 함수
def exportCSV(request):
    #크롤링한 데이터를 CSV파일로 추출하고 싶을 경우 버튼으로 할 수 있도록.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=userData.csv'},
    )
    writer = csv.writer(response)
    for key in dict_blogDatas.keys():
        writer.writerow([key, dict_blogDatas[key]['url'], dict_blogDatas[key]['content']])

    return response

#KonlPy & WordCloud를 활용한 Text분석
def konlpy(request):
    #Konlpy & Mecap
    tempResult = []
    myFile = "./csv/crawData.csv"
    with open(myFile, newline="") as csvfile:
        dataReader = csv.reader(csvfile, delimiter=",")
        for row in dataReader:
            tempResult.extend(mecab.nouns(row[2][2:]))

    #두글자 이상의 단어만 추출
    nlpResult = [i for i in tempResult if len(i)>1]

    
    ## WORDCLOUD & COUNTER

    #나만의 STOPWORD LIST로 단어 거르기.
    my_stopword_list = ["환갑", "선물", "제품", "남자", "어머니", "아버지", "때문", "우리", "나이", "관리", "생각", "부모", "정도","환갑", "제품", "도움" "우리", "가족", "엄마", "아빠", "선물", "부분", "마음", "사용", "요즘", "반전", "저희", "아버지", "어버이날", "구입", "후기"]
    for i, word in enumerate(my_stopword_list):
        STOPWORDS.add(my_stopword_list[i])

    #WordCloud를 활용한 시각화
    font_Path = "/Library/Fonts/AppleGothic.ttf"
    klines = ' '.join(row for row in nlpResult)
    stopwords = set(STOPWORDS)
    wc = WordCloud(width=800, height=800,
                   relative_scaling=0.2,
                   font_path=font_Path,
                   background_color='white',
                   stopwords=stopwords,
                   ).generate(klines)
    plt.figure(figsize=(12,12))
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")

    wc.to_file("scrapping/static/wordcloud_result.png")

    #빈도수 Counter 순위 100개까지만 담도록 함. (TOP 100 출력용.)
    #? class."collections.Counter"는 무슨 자료형일까..? 
    resultCountWords = Counter(nlpResult).most_common(n=100)

    #Make Counter CSV (판다스 분석용, 모든 데이터를 가지고 함.)
    counter_data = Counter(nlpResult)

    #Counter TOP 100 출력을 쉽게 하기 위해 배열로 바꾸어줌.
    tempAry = []
    for idx, val in enumerate(resultCountWords):
        word = f"Rank {idx+1}: {val[0]} -> {val[1]}회"
        tempAry.append(word)

    myFilePathforCSVPandas = "./csv/dataForPandas.csv"
    #카운트용 CSV 재생성 파일명 = dataForPandas , Count가 10번 이상 나온 것만 생성함.
    with open(myFilePathforCSVPandas, "w", newline="") as csvfile:
        dataWriter = csv.writer(csvfile, delimiter=",")
        dataWriter.writerow(["keyword", "count"])
        for key, val in counter_data.items():
            if val > 10:
                dataWriter.writerow([key, val])
            else:
                continue

    data = {
        "nlpResult": nlpResult,
        "wordCount": tempAry,
    }

    return render(request, 'scrapping/nlp.html', data)

#Pandas 를 활용한 데이터 시각화
def pandas(request):
    #plt 초기화 명령 plt.clf();
    plt.clf()

    myFilePath = "./csv/dataForPandas.csv"
    font_Path = "/Library/Fonts/Arial Unicode.ttf"
    font_Name = fm.FontProperties(fname=font_Path).get_name()
    matplotlib.rc("font", family=font_Name)

    df = pd.read_csv(myFilePath)
    
    #PANDAS 바
    x = df['keyword']
    y = df['count']

    plt.bar(x, y, alpha=0.5, width=0.3)
    
    #Save
    plt.savefig("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/scrapping/static/pandas_bar.png")

    ##PANDAS 누운막대그래프
    plt.clf()

    myFilePath = "./csv/dataForPandas.csv"
    font_Path = "/Library/Fonts/Arial Unicode.ttf"
    font_Name = fm.FontProperties(fname=font_Path).get_name()
    matplotlib.rc("font", family=font_Name)

    df = pd.read_csv(myFilePath)
    
    x = df['keyword']
    y = df['count']

    plt.barh(x, y)
    plt.savefig("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/scrapping/static/pandas_barh.png")


    ## PANDAS HIST
    plt.clf()
    myFilePath = "./csv/dataForPandas.csv"
    font_Path = "/Library/Fonts/Arial Unicode.ttf"
    font_Name = fm.FontProperties(fname=font_Path).get_name()
    matplotlib.rc("font", family=font_Name)

    df = pd.read_csv(myFilePath)

    plt.hist(y, bins=3)
    plt.savefig("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/scrapping/static/pandas_hist.png")
    

    #PANDAS Pie Chart
    plt.clf()

    myFilePath = "./csv/dataForPandas.csv"
    font_Path = "/Library/Fonts/Arial Unicode.ttf"
    font_Name = fm.FontProperties(fname=font_Path).get_name()
    matplotlib.rc("font", family=font_Name)

    labels = df['keyword']
    y = df['count']

    plt.pie(y, labels=labels, autopct='%.1f%%')

    plt.savefig("/Users/handonglee/Desktop/lab/coding/python/scrapPy_2021_8/scrapPy/scrapping/static/pandas_pie.png")
    

    data = {
        "bar": "hi",
        # "hist": pandasHist,
    }
    
    return render(request, 'scrapping/pandas.html', data)

