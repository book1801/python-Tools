# -*- coding: utf-8 -*-
#############################################
#
#获取并扫描可用代理
#获取地址1为：www.xicidaili.com
#获取地址2为：www.kuaidaili.com
#author:andyzhu
#date:2018/3/30
#
#############################################
import queue
import urllib.request
from lxml import etree
import threading
import os
import time
import requests

class ScanProxy:
    ############################### 全局按时 ###############################
    #保存可用的代理IP的文件
    proxyFileName="./proxy.txt"

    #准备用来抓取的代理ip池 格式："ip:port:http"
    proxyList=queue.Queue()

    #定义未检测测ip代理列表
    noCheckProxyList=queue.Queue()

    #定义要获取代理IP的URL页面列表
    spiderPageList=queue.Queue()

    #定义单个网站要抓取列表页的数量
    spiderPageCount=3

    #定义全局多线程安全锁
    lock = threading.Lock()

    ############################## function ################################
    #删除proxy.txt 文件
    #def __init__(self):
    #    if os.path.exists(self.proxyFileName):
    #        os.remove(self.proxyFileName)


    #检测代理ip是否可用 :return: boolean
    def checkProxy(self,myproxy):
        # 定义头部user-agent
        url = "http://2017.ip138.com/ic.asp"

        l = myproxy.split(":")
        ip = l[0]
        port = l[1]
        protocol = l[2]
        ipt = ip + ":" + port

        proxy = {
            'http': 'http://' + ipt,
            'https': 'https://' + ipt
        }
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Connection': 'keep-alive'}
        try:
            r = requests.get(url, headers=header, proxies=proxy, timeout=6)
            tree = etree.HTML(r.text)
        except:
            print("代理IP不可用！")
            return False
        else:
            e=tree.xpath("//center/text()")
            code=''.join(e)
            tag_start=code.find("[")
            if tag_start < 0:
                return False
            else:
                tag_start=tag_start + 1

            tag_end = code.find("]")
            if tag_end < 1:
                return False

            code_ip=code[tag_start:tag_end]

            print("ip:" + ip + "  code_ip:" + code_ip)
            if code_ip == ip:
                print("发现可用IP[ip:port]：" + ip+":"+port )
                return True

    #多线程检测noCheckProxyList(线程安全)
    def checkNewProxy(self,threadname):
        #global noCheckProxyList,proxyFileName,lock
        print(threadname+" is runing")
        while self.noCheckProxyList.qsize() > 0:
            myproxy=self.noCheckProxyList.get()
            if len(myproxy) <13:
                break
            if self.checkProxy(myproxy):
                self.proxyList.put(myproxy)

    # 通用抓取页面
    def Spider(self,url,myproxy=None):
        # 定义头部user-agent
        head = {}
        head['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"

        if myproxy == None:
            req = urllib.request.Request(url, headers=head)
            response = urllib.request.urlopen(req)
            html = response.read().decode("utf-8")
            return html
        else:
            l = myproxy.split(":")
            ip = l[0]
            port = l[1]
            protocol = l[2]
            prox = {}
            prox[ip] = port
            proxy = urllib.request.ProxyHandler(prox)
            opener = urllib.request.build_opener(proxy, urllib.request.HTTPSHandler)
            urllib.request.install_opener(opener)
            req = urllib.request.Request(url, headers=head)
            response = urllib.request.urlopen(req)
            html = response.read().decode("utf-8")
            return html

    #抓取xicidaili;   url：要抓取的URL; myproxy:字符串格式：ip:port:http
    def SpiderKuaidaili(self,url,myproxy=None):
        #global noCheckProxyList
        html=self.Spider(url,myproxy)
        tree=etree.HTML(html)
        tr = tree.xpath("//div[@id='list']/table[contains(@class,'table-bordered')]/tr[position() > 1]")
        if len(tr) > 0:
            for i in range(len(tr)):
                td = tr[i].xpath(".//td")
                if len(td) > 6:
                    ip = tr[i].xpath(".//td[1]/text()")
                    port = tr[i].xpath(".//td[2]/text()")
                    type = tr[i].xpath(".//td[4]/text()")
                    sudu = tr[i].xpath(".//td[6]/text()")

                    ip = ''.join(ip)
                    type = ''.join(type)
                    sudu = ''.join(sudu)
                    sudu = sudu.strip()
                    sudu = sudu.replace("秒", "")
                    sudu = float(sudu)
                    port = int(''.join(port))

                    if(sudu < 3):
                        line=ip+":"+str(port)+":"+type
                        self.noCheckProxyList.put(line)
        print("【抓取】" + url + "  【OK】")

    # 抓取kuaidaili;   url：要抓取的url;  myproxy：ip:port:http #
    def SpiderXicidali(self,url,myproxy=None):
        #global noCheckProxyList
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Connection': 'keep-alive'}
        html=self.Spider(url,myproxy)
        tree = etree.HTML(html)
        tr = tree.xpath("//table[@id='ip_list']/tr[position() > 1]")
        if len(tr) > 0:
            for i in range(len(tr)):
                td = tr[i].xpath(".//td")
                if len(td) > 9:
                    ip = tr[i].xpath(".//td[2]/text()")
                    port = tr[i].xpath(".//td[3]/text()")
                    type = tr[i].xpath(".//td[6]/text()")
                    sudu = tr[i].xpath(".//td[7]/div[1]/@title")

                    ip = ''.join(ip)
                    type = ''.join(type)
                    sudu = ''.join(sudu)
                    sudu = sudu.strip()
                    sudu = sudu.replace("秒", "")
                    sudu = float(sudu)
                    port = int(''.join(port))

                    if sudu < 3:
                        line = ip + ":" + str(port) + ":" + type
                        self.noCheckProxyList.put(line)
        print("【抓取】" + url + "  【OK】")

    ########################### end function ##############################

    # 读取可用代理ip文件，将代理IP加入到准备使用的代理ip池
    def StartScan(self):
        print("检测当前"+self.proxyFileName+"中的代理！")
        if not os.path.exists(self.proxyFileName):
            print(self.proxyFileName +"文件不存在，创建该文件！")
            f=open(self.proxyFileName,mode="w")
            f.close()
        for line in open(self.proxyFileName, mode="r"):
            if self.checkProxy(line):
                self.proxyList.put(line)


        #初始要抓取代理的网页列表
        for i in range(self.spiderPageCount):
            pagenum = i + 1
            url = "http://www.xicidaili.com/nn/" + str(pagenum)
            url2 = "https://www.kuaidaili.com/free/inha/" + str(pagenum) + "/"
            self.spiderPageList.put(url)
            self.spiderPageList.put(url2)


        #抓取代理ip的网页
        isUseProxy=False
        ipUserCount=0
        while self.spiderPageList.qsize() > 0:
            url=self.spiderPageList.get()
            myproxy = None
            if isUseProxy:
                myproxy = self.proxyList.get()
                self.proxyList.put(myproxy)

            if url.find("xicidaili")>0:
                self.SpiderXicidali(url,myproxy)
            elif url.find("kuaidaili")>0:
                self.SpiderKuaidaili(url,myproxy)

            if ipUserCount > 1:
                isUseProxy=not isUseProxy
                ipUserCount=0;

            n=5 - self.proxyList.qsize()
            if n > 0:
                time.sleep(n)


        #多线程检测未检测的代理ip池
        t1 = threading.Thread(target=self.checkNewProxy,name="Thread1", args=("Thread1",))
        t2 = threading.Thread(target=self.checkNewProxy,name="Thread2", args=("Thread2",))
        t3 = threading.Thread(target=self.checkNewProxy,name="Thread3", args=("Thread3",))
        t4 = threading.Thread(target=self.checkNewProxy,name="Thread4", args=("Thread4",))
        t5 = threading.Thread(target=self.checkNewProxy,name="Thread5", args=("Thread5",))
        t6 = threading.Thread(target=self.checkNewProxy,name="Thread6", args=("Thread6",))
        t7 = threading.Thread(target=self.checkNewProxy,name="Thread7", args=("Thread7",))
        t8 = threading.Thread(target=self.checkNewProxy,name="Thread8", args=("Thread8",))
        t9 = threading.Thread(target=self.checkNewProxy,name="Thread9", args=("Thread9",))
        t10 = threading.Thread(target=self.checkNewProxy,name="Thread10", args=("Thread10",))

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t9.start()
        t10.start()

        t1.join()
        print("t1 done")

        t2.join()
        print("t2 done")

        t3.join()
        print("t3 done")

        t4.join()
        print("t4 done")

        t5.join()
        print("t5 done")

        t6.join()
        print("t6 done")

        t7.join()
        print("t7 done")

        t8.join()
        print("t8 done")

        t9.join()
        print("t9 done")

        t10.join()
        print("t10 done")


        #将可用代理ip池写入文件

        print("###################开始保存代理IP到文件#####################")
        proxyListTmp=set()
        while self.proxyList.qsize() >0:
            p=self.proxyList.get()
            proxyListTmp.add(p)

        print("共获取可用代理:" + str(len(proxyListTmp)))
        file=open(self.proxyFileName,mode="w")
        while len(proxyListTmp) > 0:
            line=proxyListTmp.pop()
            line=line.replace("\n","")
            line=line.replace("\r","")
            if len(line) > 12:
                file.writelines(line+"\n")
        file.close()
        print("获取代理任务全部完成！")