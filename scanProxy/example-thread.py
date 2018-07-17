# 多线程
# -*- coding:utf-8 -*-
import threading

tickets=[]

class myThread(threading.Thread):
    def __init__(self,threadname):
        #super.__init__(self)
        threading.Thread.__init__(self)
        self.lock=threading.Lock()
        
        self.threadname=threadname

    def sale(self):
        global tickets
        while len(tickets) > 0:
            self.lock.acquire()#加锁，锁住相应的资源    
            tick=tickets.pop()
            self.lock.release()#解锁，离开该资源
            print("窗口:"+ self.threadname+"  售出:"+tick)

    def run(self):
        self.sale()


class win(object):
    def winsale(self):
        global tickets
        tickets=["n"+str(i) for i in range(1,101)]
        t1=myThread('t1')
        t2=myThread('t2')
        t3=myThread('t3')
        t4=myThread('t4')
        t5=myThread('t5')

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()

        print("多线程运行完成！")

w=win()
w.winsale()
