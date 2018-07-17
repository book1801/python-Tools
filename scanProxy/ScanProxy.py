# -*- coding:utf-8 -*-
# 西祠代理扫描
import threading
import requests
import time
from lxml import etree
import pdb

ScanProxyList=[] #待检测的代理列表
urllist=["http://www.xicidaili.com/nn/"+str(page) for page in range(1,11)]
ProxyCount=1 #要获取的有效代理数量

class ScanProxy(threading.Thread):
    ProxyList=[] #可用代理列表
    __ScanedProxyList={} #无效代理列表
    
    __proxyfile="./no_proxy_list.txt"
    __resultProxyFile="./use_proxy_list.txt"

    def __init__(self):
        self.readOldProxy()
        threading.Thread.__init__(self)

    def setProxyCount(self,count):
        global ProxyCount
        ProxyCount=count

    def getProxyCount(self):
        global ProxyCount
        return ProxyCount    

    def readOldProxy(self):
        value=1
        for line in open(self.__proxyfile,mode="r",encoding="utf-8"):
            line=line.replace("\n","")
            arr=line.split(":")
            if len(arr) > 2:
                ip=arr[0]
                port=arr[1]
                https=arr[2]
                key=ip+":"+port+":"+https
                self.__ScanedProxyList[key]=value
                value=value+ 1

    #将代理写入文件
    def writeProxy(self):
        #按字典键值对字典进行排序
        tmp_list=sorted(self.__ScanedProxyList.items(),key=lambda e:e[1],reverse=True)
        file=open(self.__proxyfile,mode="w",encoding="utf-8")
        n=1
        for k,v in tmp_list:
            if n > 10000: break
            line=k
            file.writelines(line+"\n")
            n=n +1
        file.close() 

    #检测代理
    def scanProxy(self,ipporthttps):
        url = "http://2017.ip138.com/ic.asp"
        arr=ipporthttps.split(":")
        if len(arr) > 2:
            ip=arr[0]
            port=arr[1]
            #https=arr[2]

            ipport = ip + ":" + port
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                'Connection': 'keep-alive'
                }
            proxy = {
                'http': 'http://' + ipport,
                'https': 'https://' + ipport
                    }
            try:
                r = requests.get(url, headers=header, proxies=proxy, timeout=6)
                tree = etree.HTML(r.text)
            except:
                print("【测试】"+ipporthttps + " 不可用")
                return False
            else:
                e=tree.xpath("//center/text()")
                code=''.join(e)
                tag_start=code.find("[")
                if tag_start < 0:
                    print("【测试】"+ipporthttps + " 不可用")
                    return False
                else:
                    tag_start=tag_start + 1

                tag_end = code.find("]")
                if tag_end < 1:
                    print("【测试】"+ipporthttps + " 不可用")
                    return False

                code_ip=code[tag_start:tag_end]

                print("ip:" + ip + "  code_ip:" + code_ip)
                if code_ip == ip:
                    print("【测试】"+ipporthttps + " OK")
                    return True
        else:
            print("【检测】ip:port:https 格式不正确")

    #扫描西祠代理    
    def spiderXici(self,url):
        header={}
        header["User-Agent"]="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        header["Host"]="www.xicidaili.com"
        print("【抓取】"+url)
        try:
            r=requests.get(url,headers=header,timeout=6)
            html=r.text
            return html
        except:
            return ""

    #解析西祠代理页面
    def getXiciProxy(self,html):
        global ScanProxyList
        e=etree.HTML(html)
        tr=e.xpath("//table[@id='ip_list']/tr[position() >1]")
        for e_tr in tr:
            td=e_tr.xpath(".//td")
            if len(td) > 9:
                ip=td[1].xpath("string(.)")
                port=td[2].xpath("string(.)")
                https=td[5].xpath("string(.)")
                ipporthttps=ip+":"+port+":"+https

                if (ipporthttps not in ScanProxyList) and (ipporthttps not in self.__ScanedProxyList) and (ipporthttps not in self.ProxyList):
                    ScanProxyList.append(ipporthttps)

    #多线程扫描
    def run(self):
        global urllist,ScanProxyList,ProxyCount #list是线程安全的，
        while len(self.ProxyList) < ProxyCount:
            if len(urllist) > 0:
                url=urllist.pop()
                html=self.spiderXici(url)
                if html=="":
                    urllist.append(url)
                    time.sleep(5*60)
                else:
                    self.getXiciProxy(html)

            if len(ScanProxyList) < 1:
                break
            else:
                ipporthttps=ScanProxyList.pop()
                result=self.scanProxy(ipporthttps)
                if result:
                    self.ProxyList.append(ipporthttps)
                else:
                    self.__ScanedProxyList[ipporthttps]=len(self.__ScanedProxyList)    

            
                  