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
import datetime

# URL을 담을 공간
page_index_urls = []
blog_urls = []
blog_contents = []
dict_blogDatas = {}
userReqKeyword = ""

def index(request):
    data = {
        "msg": "아래 입력창에 필요한 정보를 입력하면 크롤링을 시작합니다."
    }
    return render(request, 'scrapping/index.html', data)

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

    #사용자가 요청한 내용대로, pageNumber를 매개변수로잡고, 키워드를 "백산수"로 잡은 결과
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

def scrapPage(request):
    #크롤링 페이지에서 가져온 블로그 URL들을 scrapping해서, 필요한 데이터 추출(iframe 주의 할 것)
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

    data = {
        "blogContent": dict_blogDatas
    }

    return render(request, 'scrapping/scrap.html', data)

def exportCSV(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="crawData.csv"'},
    )
    writer = csv.writer(response)
    for key in dict_blogDatas.keys():
        writer.writerow([key, dict_blogDatas[key]['url'], dict_blogDatas[key]['content']])

    return response