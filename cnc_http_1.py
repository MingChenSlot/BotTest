#coding:UTF-8
import urllib
import sys, os, time
from threading import Thread
import socket 
socket.setdefaulttimeout(10)    #设置10s后连接超时

def http_commu(url, delay, logs):
    # http://localhost:8000/ip/test?id=1
    time.sleep(delay)
    try:
        task = urllib.urlopen(url).read()
        logs['type'] = 'INFO'
        logs['msg'] = 'get message from %s successfully.' % url
        return task, logs
    except:
        logs['type'] = 'ERROR'
        logs['msg'] = 'unable to connect to %s.' % url
        return '', logs

def read_stdin():
    # 检查输入
    cmd = sys.stdin.readline().strip()
    if cmd == 'STOP':
        sys.stdout.write("LOG, INFO, The module is stopped.\n")
        os._exit(1)

'''
    argv:    param1: url
             param2: delay1
             param3: delay2
             param4: delay3
             ……
             paramN: delayN
'''
if __name__ == '__main__':
    # print sys.argv
    logs = {}
    task = ''
    buf = ''
    delay_time = []
    for i in range(len(sys.argv) - 2):
        if sys.argv[2+i] != 'None':
            delay_time.append(int(sys.argv[2+i]))
    
    t_read = Thread(target = read_stdin, args = ())
    t_read.start()
    while(True):
        for dl in delay_time:   
            # 获取命令
            buf, logs = http_commu(sys.argv[1], dl, logs)
            sys.stdout.write("LOG, %s, %s\n"%(logs['type'], logs['msg']))        
            if (not buf) or (buf == task):
                pass
            else:
                cmd_msg = buf.split('|')
                while len(cmd_msg) < 7:
                    cmd_msg.append(' ')
                cmd_msg = ','.join(cmd_msg)
                sys.stdout.write("CMD,%s\n"%cmd_msg)
                task = buf
            sys.stdout.flush()
    
    t_read.join()       
            
            
    

