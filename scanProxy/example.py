#这里是ScanProxy的使用实例，这里开启了5个线程，获取是个有用的代理
from ScanProxy import ScanProxy
import sys

t1=ScanProxy()
t2=ScanProxy()
t3=ScanProxy()
t4=ScanProxy()
t5=ScanProxy()
t1.setProxyCount(10) #定义要获取的可用的代理数量，默认为1，
print(t1.getProxyCount())
sys.exit(0)

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
