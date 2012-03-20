#coding:UTF-8
import urllib
import sys, os 
import re
from threading import Thread

def get_ip_info(url, ip):
    s = urllib.urlopen('%s?ip=%s&action=2'%(url, ip)).read()
    lis = re.findall(r"(?<=<li>).*?(?=</li>)", s)
    return lis[0][12:].decode('gbk').encode('utf8')

#ip int to ip String express
def num2ipstr(num):
    myip = []
    myip.append(str(num/16777216))
    myip.append(str((num%16777216)/65536))
    myip.append(str((num%65536)/256))
    myip.append(str(num%256))
    return '.'.join(myip)

def read_stdin():
    # 检查输入
    cmd = sys.stdin.readline().strip()
    if cmd == 'STOP':
        sys.stdout.write("LOG, INFO, The module is stopped.\n")
        os._exit(1)

if __name__ == '__main__':
    print sys.argv
    logs = {}
    num_start = 16777216
    num_end = 4294967295
    
    t_read = Thread(target = read_stdin, args = ())
    t_read.start()
    for i in range(num_start, num_end, 256):
        logs['type'] = 'INFO'
        logs['msg'] = '%s %s'%(num2ipstr(i), get_ip_info('http://ip138.com/ips.asp', num2ipstr(i)))
        sys.stdout.write("LOG, %s, %s\n"%(logs['type'], logs['msg']))
        sys.stdout.flush()
    