# -*- coding:utf-8 -*-
import requests
import random
import re
import os
import urllib.parse
from mydb import MyDB
from lxml import etree
from ScanProxy import ScanProxy
import pdb

############## Config ################################
keyword="手机赚钱软件" #搜索的关键词
maxPage=100 #抓取的最大列表页页码
############## End Config ############################

############## Public Var ############################
urlList=[]
proxyList=[]
history_urlList=[]
db=MyDB()
############## End Public ############################

############## Function ##############################
def userAgentRand():
    l=[]
    l.append("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36")
    l.append("Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/61.0")
    l.append("Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)")
    l.append("Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1")
    l.append("Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)")
    l.append("Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)")

    return random.sample(l,1)[0]

def spider(url,ipx=""):
    header={}
    header['User-Agent']=userAgentRand()
    header['Connection']="keep-alive"

    try:
        if ipx=="":
            print("【抓取】"+url)
            r=requests.get(url,headers=header,timeout=6)
        else:
            arr=ipx.split(":")
            if len(arr) >1:
                ip=arr[0]
                port=arr[1]
                ipport=ip+":"+port
                proxy = {'http': 'http://' + ipport,'https': 'https://' + ipport}
                print("【抓取】 proxy:"+ipport + "   url:" + url)
                r=requests.get(url,headers=header,proxies=proxy,timeout=6)
            else:
                r=requests.get(url,headers=header,timeout=6)
        return r.text        
    except:
        return ""

#向抓取列表中添加待抓取URL
def addUrl(url):
    global urlList
    if url not in urlList:
        urlList.append(url)

#从待抓取列表中随机获取一个URL
def getUrl():
    global urlList
    if len(urlList) > 0:
        return random.sample(urlList,1)[0]
    else:
        return ""    

#从待抓取列表中删除指定url
def delUrl(url):
    global urlList
    if urlList.count(url) > 0:
        urlList.remove(url)

#解析搜索列表页，从列表页中抽取详情页URL
def pasteListPage(html):
    e=etree.HTML(html)
    href=e.xpath("//li[@class='item']/div[@class='qa-i-hd']/h3/a")
    #import pdb
    #pdb.set_trace()
    print("【抽取】共抽取url链接 " +str(len(href)) + "  个")
    for e_href in href:
        url=e_href.xpath("string(@href)")
        url="http://wenda.so.com"+url
        if url not in history_urlList:
            print("【添加】添加 "+url+"  到待抓取列表")
            addUrl(url)
    return len(href)    


#解析详情页
def pasteQuestionPage(html):
    print("【解析】解析问答详情页")
    e=etree.HTML(html)
    title=e.xpath("string(//div[@class='hd']/h2[contains(@class,'js-ask-title')])")
    e_content=e.xpath("//div[contains(@class,'resolved-cnt')]")
    if (type(e_content)==list) and (len(e_content) > 0):
        e_content=e_content[0]
    try:    
        content_html=etree.tostring(e_content,encoding="unicode")
    except:
        #被span
        return "",""   
    content_html=content_html.replace("<br>","#<br#").replace("<p>","#p#").replace("</p>","#/p#")
    dr = re.compile(r'<[^>]+>',re.S)
    content_html = dr.sub('',content_html)
    content_html=content_html.replace("#br#","<br>").replace("#p#","<p>").replace("#/p#","</p>")
    return title,content_html


#抓取历史记录初始化
def UrlListInit():    
    global db,history_urlList,urlList
    history_urlList=db.getUrlAll(True)
    urlList=db.getUrlAll(False)

#多线程扫描代理过程
def startScanProxy():
    global proxyList
    print("开始多线程代理扫描")
    os.system("python ThreadScanProxy.py")
            
    #读取代理信息列表文件
    proxyfile="proxy.list"
    if os.path.isfile(proxyfile):
        proxyList=[]
        for l in open(proxyfile,mode="r",encoding="utf-8"):
            proxyList.append(l.replace("\n","")) 

#判断当前抓取是否被SPAN
def isSpan(html):
    if html=="":
        return False #抓取页面发送异常
    else:
        e=etree.HTML(html)
        title_str=e.xpath("string(//title)")
        if (title_str.find("_360问答") > 0) and (title_str.find("反作弊页面") <0):
            return True
        else:
            return False               
############## End Function ###########################


############## Main Appaction #########################
#读取正常抓取的历史记录
print("读取正常抓取的历史记录")
UrlListInit()

#新任务第一次运行，进行urlList初始化
if len(urlList) < 1:
    print("开始生成要抓取搜索列表页URL")
    estr=urllib.parse.quote(keyword)
    for page in range(maxPage):
        urlList.append("http://wenda.so.com/search/?q="+estr+"&pn="+str(page))



#开始抓取
print("开始抓取")
SPAN_COUNT=0
while len(urlList) > 0:
    url=getUrl()

    if url in history_urlList:
        print("【过滤】url 已经在被抓取过。")
        delUrl(url)
        continue

    ipx=""

    if len(proxyList) > 0:
        ipx=proxyList.pop()
        SPAN_COUNT=0 #新代理重新计数

    html=spider(url,ipx)
    #检测是否被SPAN
    if isSpan(html):
        SPAN_COUNT=0
        if ipx!="":
            proxyList.append(ipx)
    else:
        SPAN_COUNT=SPAN_COUNT + 1
        print("抓取出现异常: " + str(SPAN_COUNT) +" 次")
        if SPAN_COUNT > 3:
            #开启代理扫描
            print("检测到被360 SPAN,进行数据保存")
            result1=db.saveUrl(urlList,False,True)
            result2=db.saveUrl(history_urlList,True,False)
            if result1 and result2:
                print("urllist数据保存完成")
            else:
                print("【异常】urllist数据保存出现异常")    
            
            #多线程代理扫描
            startScanProxy()
            SPAN_COUNT=0
        continue        


    #通过检测，进行页面解析
    if url.find("search") > 0:
        pasteListPage(html)
    else:
        title,content=pasteQuestionPage(html)
        qid=url.replace("wenda.so.com/q/","").replace("/","").replace("http:","").replace("https:","")
        print(qid)
        print(title)
        print(content)
        #pdb.set_trace()
        db.insert(url,qid,title,content)

    #对url进行处理
    history_urlList.append(url)
    delUrl(url)
    SPAN_COUNT=0




    '''
    #pdb.set_trace()
    if html=="":
        SPAN_COUNT =SPAN_COUNT + 1
        print("抓取出现异常: " + str(SPAN_COUNT) +" 次")
        continue
    else:
        #ipx持续可用，继续加入列表
        if ipx!="":
            tmp_e=etree.HTML(html)
            title_str=tmp_e.xpath("string(//title)")
            if title_str.find("_360问答") >=0:
                proxyList.append(ipx)
                SPAN_COUNT=0 #当代理持续可用时，标记为0
        
    if SPAN_COUNT >3:
        if len(proxyList) > 0:
            continue
        else:
            #开启代理扫描
            print("检测到被360 SPAN,进行数据保存")
            result1=db.saveUrl(urlList,False,True)
            result2=db.saveUrl(history_urlList,True,False)
            if result1 and result2:
                print("urllist数据保存完成")
            else:
                print("【异常】urllist数据保存出现异常")    
            
            #多线程代理扫描
            startScanProxy()
            SPAN_COUNT=0
            continue


    if url.find("search") > 0:
        count=pasteListPage(html)
    else:
        title,content=pasteQuestionPage(html)
        if title=="":
            print("检测到进入360反作弊页面")
            
            SPAN_COUNT=4
            continue
        else:    
            qid=url.replace("wenda.so.com/q/","").replace("/","").replace("http:","").replace("https:","")
            print(qid)
            print(title)
            print(content)
            db.insert(url,qid,title,content)

    #对url进行处理
    history_urlList.append(url)
    delUrl(url)
    SPAN_COUNT=0
    '''