# -*- coding:utf-8 -*-

import re
import sys
import csv
import time
import urllib
import urllib2
import requests
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

def BrowserHeaders():
    head    = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/' \
           '537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
    headers = {'User-Agent': head}
    return headers

def GetTag():
    BaseUrl = 'https://movie.douban.com/tag/'
    headers = BrowserHeaders()
    try:
        request  = urllib2.Request(BaseUrl)
        response = urllib2.urlopen(request)
        soup     = BeautifulSoup(response,"lxml")
    except Exception, e:
        print "maybe blocked!"
        return False
    for items in soup.find_all('table',{'class':'tagCol'}):
        taglist = re.findall(r'<td><a href="/tag/.*?">(.*?)</a><b>.*?</b></td>', str(items))
        for tag in taglist:
            GetFilmPage(tag, 400)
    return True

def GetFilmPage(TagName, pangeNumber):
    TagUrl  = 'https://movie.douban.com/tag/{tag}?start={start}&type=T'
    headers = BrowserHeaders()
    for pages in range(pangeNumber):
        print TagName
        print "    crawling page%d..." % (pages + 1)
        #time.sleep(6)
        startNum = pages * 20
        Tagurl   = TagUrl.format(start = startNum, tag = urllib.quote(TagName))
        try:
            request  = urllib2.Request(Tagurl, headers = headers)
            response = urllib2.urlopen(request)
            tagsoup  = BeautifulSoup(response,"lxml")
        except Exception, e:
            print "    maybe blocked!"
            continue
        for items in tagsoup.find_all('a',{'class':'nbg'}):
            filmurllist = re.findall(r'<a class="nbg" href="(.*?)" title=".*?">', str(items))
            for FilmUrl in filmurllist:
                #print FilmUrl
                if GetComments(FilmUrl) == False:
                    continue
    return True


def GetComments(urlComments):
    commentcomplete = []
    headers  = BrowserHeaders()
    nextpage = "comments?start={commentNum}&limit=20&sort=new_score"
    for commentPages in range(11):
        print "        crawling comment page%d..." % (commentPages + 1)
        time.sleep(2)
        pageNum = commentPages * 20 
        SingleCommentsPage = nextpage.format(commentNum = pageNum)
        try:
            request     = urllib2.Request(urlComments + SingleCommentsPage, headers= headers)
            response    = urllib2.urlopen(request)
            commentSoup = BeautifulSoup(response, "lxml")
        except Exception, e:
            print "        maybe blocked!"
            return False
        for commentsDetail in commentSoup.find_all('div',{'class':'comment'}):
            #get userid
            userID = re.search(r'<a class=.*?href="https.*?">(.*?)</a>.*?', str(commentsDetail))
            if userID != None:
                userID = userID.group(1).decode('utf8')
                #print userID
            #get rate
            rate = re.search(r'<span class="allstar(.*?) rating" title=".*?"></span>.*?', str(commentsDetail))
            if rate != None:
                rate = rate.group(1)
                #print rate
            #get comment
            commentText = commentsDetail.p.text
            item = [userID, rate, commentText]
            commentcomplete.append(item)
            Writecsv(commentcomplete)
            commentcomplete.pop()


def Writecsv(commentcomplete):
    with open('comment.csv', 'ab+') as f:
        writer = csv.writer(f)
        for singlecomment in commentcomplete:
            writer.writerow(singlecomment)
    f.close()



GetTag()