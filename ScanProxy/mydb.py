# -*- coding:utf-8 -*-
import pymysql

class MyDB(object):
    cn=None
    cursor=None

    #初始化连接数据库
    def __init__(self):
        self.cn=pymysql.connect(host="localhost",user="root",password="root",database="szproject",charset="utf8")
        self.cursor=self.cn.cursor()

    #添加数据到数据库
    def insert(self,url,qid="",title="",content=""):
        sql="insert into question (url,qid,title,content) values('"+url+"','"+qid+"','"+title+"','"+content+"')"
        try:
            self.cursor.execute(sql)
            self.cn.commit()
            print("插入数据成功！")
        except:
            print("插入数据到数据库出现异常！")
            self.cn.rollback()
        
    
    #判断qid是否存在
    def isFoundQid(self,qid):
        sql="select count(*) from question where qid='"+qid+"'"
        self.cursor.execute(sql)
        count=self.cursor.fetchone()
        if count[0] > 0:
            return True
        else:
            return False    

    #保存url地址池
    def saveUrl(self,urllist,status,clear):
        try:
            if clear:
                sql="delete from haosourllist"
                self.cursor.execute(sql)
                self.cn.commit
            if status:
                for url in urllist:
                    sql="insert into haosourllist (url,status) values('"+url+"','1')"
                    self.cursor.execute(sql)
                    self.cn.commit 
            else:    
                for url in urllist:
                    sql="insert into haosourllist (url,status) values('"+url+"','0')"
                    self.cursor.execute(sql)
                    self.cn.commit
            
            return True       
        except:
            print("保存URL地址池失败！") 
            return False       


    #获取全部url地址池
    def getUrlAll(self,status):
        urllist=[]
        sql="select url,status from haosourllist "
        if status:
            sql=sql+" where status='1'"
        else:
            sql=sql+" where status='0'"    
        self.cursor.execute(sql)
        data=self.cursor.fetchall()
        for t in data:
            url,status=t
            if url not in urllist:
                urllist.append(url)
        return urllist

    #析构函数，关闭连接
    def __del__(self):
        self.cursor=None
        self.cn=None         