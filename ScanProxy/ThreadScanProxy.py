#-*-coding:utf-8 
#多线程代理扫描
import threading
import requests
import pdb
from lxml import etree

ProxyList=[]
ScanProxyList=[]
class ScanProxy(threading.Thread):
    UrlList=[]
    def __init__(self):
        self.InitUrlLis()
        threading.Thread.__init__(self)

    def InitUrlLis(self):
        self.UrlList.append("http://www.xicidaili.com/nn/")
        self.UrlList.append("http://www.ip3366.net/")
        self.UrlList.append("http://www.iphai.com/free/ng")


    #抓取页面
    def spider(self,url,ipt):
        print("【抓取】"+url)
        header={}
        header["User-Agent"]="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        try:
            if (ipt != "") and (len(ipt.split(":")) > 1):
                arr=ipt.split(":")
                ip=arr[0]
                port=arr[1]
                ipport=ip+":"+port
                proxy = {'http': 'http://' + ipport,'https': 'https://' + ipport}
                r=requests.get(url,headers=header,proxies=proxy,timeout=6)
                html=r.text
                return html
            else:
                r=requests.get(url,headers=header,timeout=6)
                html=r.text
                return html    
        except:
            return ""       
    

    #解析西祠页面
    def getXiciPage(self,html):
        global ScanProxyList
        e=etree.HTML(html)
        tr=e.xpath("//table[@id='ip_list']/tr[position() >1]")
        for e_tr in tr:
            td=e_tr.xpath(".//td")
            if len(td) > 9:
                ip=td[1].xpath("string(.)")
                port=td[2].xpath("string(.)")
                ipport=ip+":"+port
                if ipport not in ScanProxyList:
                    ScanProxyList.append(ipport)          

    #解析ip3366
    def getIp3366Page(self,html):
        global ScanProxyList
        e=etree.HTML(html)
        tr=e.xpath("//table/tbody/tr")
        for e_tr in tr:
            td=e_tr.xpath(".//td")
            if len(td) > 7:
                ip=td[0].xpath("string(.)")
                port=td[1].xpath("string(.)")
                ipport=ip+":"+port
                if ipport not in ScanProxyList:
                    ScanProxyList.append(ipport)           

    #解析iphai
    def getIphaiPage(self,html):
        global ScanProxyList
        e=etree.HTML(html)
        tr=e.xpath("//table/tr[position() >1]")
        for e_tr in tr:
            td=e_tr.xpath(".//td")
            if len(td) > 6:
                ip=td[0].xpath("string(.)").replace("\r\n","").replace(" ","")
                port=td[1].xpath("string(.)").replace("\r\n","").replace(" ","")
                ipport=ip+":"+port
                if ipport not in ScanProxyList:
                    ScanProxyList.append(ipport)

    #检测代理可用性    扫描ip138
    '''
    def scan(self,ipt):
        url = "http://2018.ip138.com/ic.asp"
        arr=ipt.split(":")
        if len(arr) > 1:
            ip=arr[0]
            port=arr[1]

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
                print("【检测】"+ipport + " 不可用")
                return False
            else:
                code=tree.xpath("string(//center)")
                #pdb.set_trace()
                if code.find("["+ip+"]") >=0:
                    print("【检测】"+ipport + "  OK ")
                    return True
                else:
                    print("【检测】"+ipport + " 不可用")
                    return False    
                
        else:
            print("【检测】ip:port 格式不正确")
            return False 
    '''
    def scan(self,ipt):
        url = "https://www.so.com/"
        arr=ipt.split(":")
        if len(arr) > 1:
            ip=arr[0]
            port=arr[1]

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
                #print("【检测】"+ipport + " 不可用")
                return False
            else:
                code=tree.xpath("string(//title)")
                #pdb.set_trace()
                if (code.find("360搜索") >=0) and (code.find("SO靠谱") > 0):
                    #print("【检测】"+ipport + "  OK ")
                    return True
                else:
                    #print("【检测】"+ipport + " 不可用")
                    return False    
                
        else:
            print("【检测】ip:port 格式不正确")
            return False     

    #扫描过程
    def startSpider(self):
        for url in self.UrlList:
            html=self.spider(url,"")
            if html=="":
                print("【异常】抓取 "+url+" 出现异常.")
            else:
                if url.find("xicidaili") >= 0:
                    self.getXiciPage(html)
                elif url.find("ip3366") >=0:
                    self.getIp3366Page(html)
                elif url.find("iphai")  >=0:
                    self.getIphaiPage(html)
                else:
                    print("【异常】 找不到该页面"+url+" 的解析方法.")
    
    #多线程扫描
    def run(self):
        global ScanProxyList,ProxyList
        while len(ScanProxyList):
            p=ScanProxyList.pop()
            
            if self.scan(p):
                print(threading.current_thread().getName()+"  " + p +"  OK")
                if p not in ProxyList:
                    ProxyList.append(p)
            else:
                print(threading.current_thread().getName()+"  " + p +"   不可用")
                if p in ProxyList:
                    ProxyList.remove(p)

    #获取扫描结果
    def getResultProxy(self):
        global ProxyList
        return ProxyList

    #展示扫描结果
    def showProxy(self):
        global ProxyList
        for proxy in ProxyList:
            print(proxy)

############ test ############
s1=ScanProxy()
s1.startSpider()

s2=ScanProxy()
s3=ScanProxy()
s4=ScanProxy()
s5=ScanProxy()
s6=ScanProxy()
s7=ScanProxy()
s8=ScanProxy()
s9=ScanProxy()
s10=ScanProxy()

s1.start()
s2.start()
s3.start()
s4.start()
s5.start()
s6.start()
s7.start()
s8.start()
s9.start()
s10.start()

s1.join()
s2.join()
s3.join()
s4.join()
s5.join()
s6.join()
s7.join()
s8.join()
s9.join()
s10.join()

result=s1.getResultProxy()
file="./proxy.list"
f=open(file,mode="w",encoding="utf-8")
for l in result:
    l=l+"\n"
    f.writelines(l)
f.close()    

