#coding:UTF-8
import time
import sys
import os
import socket
from threading import Thread
import MySQLdb.cursors
import subprocess

def get_sys_info():
    sys = os.name
    ipaddr = socket.gethostbyname(socket.gethostname()) # 获得本机IP
    os_info = os.environ['OS'] # 获得操作系统信息
    
    if sys == 'nt':
        hostname = os.getenv('computername')
        return hostname, ipaddr, os_info

    elif sys == 'posix':
        host = os.popen('echo $HOSTNAME')
        try:
            hostname = host.read()
            return hostname, ipaddr, os_info
        finally:
            host.close()
    else:
        return 'Unkwon hostname', ipaddr, os_info


class BotMaster():
    def __init__(self, dbhost, dbuser, dbname, dbpass=''):
        self.host = dbhost 
        self.user = dbuser 
        self.db = dbname 
        self.passwd = dbpass
        
    def connect(self):
        try:
            con = MySQLdb.connect(  host = dbhost, 
                                        user = dbuser, 
                                        db = dbname, 
                                        passwd = dbpass, 
                                        charset="utf8",
                                        cursorclass = MySQLdb.cursors.Cursor
                                           )
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit (1)
        return con
    
    def register_me(self, botname, hostname, ipaddr, os_info, t_update = 5): 
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
        con = self.connect()
        cursor = con.cursor() 
        # 检查botname冲突
        checkSQL = 'select count(*) from bots where bot = %s and ts_down <= 0'
        cursor.execute(checkSQL, botname)
        count_result = cursor.fetchone()[0]
        # print count_result
        # 注册自己
        if count_result <= 0:
            registerSQL = 'insert into bots \
                            (bot, info_ip, info_hostname, info_os, ts_up, ts_lastact) \
                            values \
                            (%s, inet_aton(%s), %s, %s, %s, %s)'
            cursor.execute(registerSQL, (botname, ipaddr, hostname, os_info, str(now), str(now)))
            con.commit()  
        # 刷新状态
        while True:
            time.sleep(t_update)
            now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
            updateSQL = 'update bots \
                        set ts_lastact = %s where bot = %s and ts_down <= 0' 
            cursor.execute(updateSQL, (now, botname))
            con.commit()
    
    '''
        调用模块, 并读取模块返回的LOG和CMD信息，写入MySQL数据库
    '''
    def call_mod(self, task, botname):
        # Debug
        # print task
        con = self.connect()
        cursor = con.cursor() 
        process = subprocess.Popen("python %s.py %s %s %s %s %s"%
                                   (task[2], task[3], task[4], task[5], task[6], task[7]), 
                                   shell=False, 
                                   bufsize = 0,
                                   stdin = subprocess.PIPE, 
                                   stdout = subprocess.PIPE, 
                                   stderr=subprocess.STDOUT)
        while True:            
            sql = 'select count(*) from tasks \
                    where id = %s and cancelled = TRUE'
            cursor.execute(sql, task[0])
            count_result = cursor.fetchone()[0]
            if count_result > 0:
                process.stdin.write('STOP')
                break
            else:
                process.stdin.write('CONTINUE')
                
            drawback = process.stdout.readline()
            # Debug
            print drawback
            if drawback:
                drawback_list = drawback.split(',')
                now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
                if drawback_list[0] == 'LOG':
                    logSQL = 'insert into logs(bot, module, ts, type, message) \
                              values \
                              (%s, %s, %s, %s, %s)'
                    cursor.execute(logSQL, 
                                   (botname, task[2], now, drawback_list[1], drawback_list[2]))
                    con.commit()
                elif drawback_list[0] == 'CMD':
                    cmdSQL = 'insert into tasks(bot, module, param_1, \
                                                param_2, param_3, param_4, \
                                                param_extra, source, ts_created)\
                              values\
                              (%s, %s, %s, %s, %s, %s, %s, %s, %s) '
                    cursor.execute(cmdSQL, 
                                   (botname, drawback_list[1], drawback_list[2], 
                                    drawback_list[3], drawback_list[4], 
                                    drawback_list[5], drawback_list[6], 
                                    task[2], str(now)))
                    con.commit()
                else:
                    sys.stderr.write("Unknown Output from Module %s\n"%task[1])
            time.sleep(2)   #这个可以改
                
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sql = 'update tasks \
               set ts_finish = %s where id = %s' 
        print 'end of the module %s'%task[2]
        cursor.execute(sql, (now, task[0]))
        con.commit()
        cursor.close()
        con.close()
    
    '''
        从task表中读取任务，并调用相应模块
    '''    
    def exec_task(self, botname, t_requery = 30):
        con = self.connect()
        cursor = con.cursor() 
        current_task_id = -1
        while True:
            sql = 'select id, bot, module, param_1, param_2, \
                          param_3, param_4, param_extra \
                    from tasks \
                    where bot = %s and ts_begin = 0 and cancelled = FALSE\
                    order by id'
            cursor.execute(sql, botname)
            task_list = cursor.fetchall()
            print 'task list', task_list
            for task in task_list:
                current_task_id = task[0]
                now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                updateSQL = 'update tasks \
                            set ts_begin = %s where id = %s'
                cursor.execute(updateSQL, (now, current_task_id))
                con.commit()
                t = Thread(target=self.call_mod, args=(task,botname,))  # 调用新线程驱动模块
                t.start() 
            time.sleep(t_requery)
        

if __name__ == "__main__":    
    script, botname, dbhost, dbport, dbuser, dbpass, dbname = sys.argv
    host, ipaddr, os_info = get_sys_info()

    master = BotMaster(dbhost, dbuser, dbname, dbpass) 
    
    reg = Thread(target = master.register_me, args = (botname, host, ipaddr, os_info, ))
    reg.start()
    master.exec_task(botname)  
    
    reg.join()

    print 'done'