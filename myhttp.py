#!/usr/bin/python3
# -*- coding:utf-8 -*-
#auth:zhiyi
import socket
import os
import asyncio
from configparser import ConfigParser
import logging
from time import perf_counter
import sys

class http_server(object):
    def __init__(self):

        self.cfg = ConfigParser()  # 实例化配置文件
        self.cfg.read('httpconfig.ini')
        self.ipaddress = self.cfg.get('network', 'ip_address')
        self.port = self.cfg.getint('network','port')
        #self.documents_root = self.cfg.get('dir', 'documents_root')

        self.http_socket = socket.socket(socket.AF_INET)  # 初始化套接字
        self.http_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)  # 让套接字复用未释放端口
        self.http_socket.bind((self.ipaddress,self.port))  # 绑定 IP 和端口
        self.response_header = []
        #self.documents_root = './html'

        self.g_templates_dir = './templates'
        self.g_dynamic_dir = './dynamic'
        self.g_static_dir = './static'

        sys.path.append(self.g_dynamic_dir)

        logging.basicConfig(filename='myhttpd.log', level=logging.INFO, format='%(levelname)s:%(asctime)s:%(message)s')




    def run_server(self):
        logging.info('httpd server is started')
        self.loop = asyncio.get_event_loop()
        self.http_socket.listen(128)  # 监听端口
        while True:
            client_conn, client_ip = self.http_socket.accept() #接受客户请求
            #为请求创建一个线程
            task = self.loop.create_task(self.handle_request(client_conn))
            self.loop.run_until_complete(task)



    async def handle_request(self,client_conn):
        # 接受请求数据
        starttime = perf_counter()
        request = client_conn.recv(2048)
        if not request:
            client_conn.close()
            return
        else:
            request_method,request_url = self.analysis_request(request)
            #self.logging.info('%s  %s  %s',self.client_ip,self.request_method,self.request_url)  # 增加记录日志功能
            logging.info('%s  %s  %s',client_conn.getpeername(),request_method,request_url)  # 增加记录日志功能
            #self.log.info('aaaaaa')
            if request_method == 'GET':
                #print(client_conn.getpeername(),request_method,request_url)
                await self.handle_GET_method(client_conn,request_url,starttime)


    def analysis_request(self,request):
        request_tmp = request.decode('utf-8')
        #print(request_tmp)
        request_header, *request_bodys = request_tmp.splitlines()
        request_method, request_url, http_version = request_header.split()
        # print(request_bodys)
        #print(request_method,request_url,self.client_ip)
        return request_method, request_url

    async def handle_GET_method(self,client_conn,request_url,starttime):
        if request_url == '/':
            request_url = '/index.html'
        if not request_url.endswith('.py'):
            file_name = self.g_static_dir + request_url
            print('-' * 50)
            print(file_name)
            print('-' * 50)
            if os.path.exists(file_name):
                with open(file_name, 'rb') as f:
                    content = f.read()
                await asyncio.sleep(0.001)
                response_header = 'HTTP/1.1 200 OK\r\n'  # 编辑响应头
                response_header += 'Content_Length: %d\r\n' % len(content)
                response_header += '\r\n'  # 追加响应头分割
                response_body = content  # 编辑响应体
                # 发送响应数据
                try:
                    client_conn.send(bytes(response_header, encoding='gbk'))
                    client_conn.send(response_body)
                    await asyncio.sleep(0.001)
                    endtime = perf_counter()
                    print(endtime - starttime)
                except Exception as e:
                    print('发送数据错误')
                    logging.error('e')
            else:
                with open('./templates/404.html', 'rb') as f:
                    content = f.read()
                    await asyncio.sleep(0.001)
                response_header = 'HTTP/1.1 404 Not Found\r\n'
                response_header += 'Content_Length: %d\r\n' % len(content)
                response_header += '\r\n'  # 追加响应头分割

                response_body = content
                client_conn.send(bytes(response_header, encoding='gbk'))
                client_conn.send(response_body)
                await asyncio.sleep(0.001)
        else:
            self.frame = __import__('myapp')
            #app = getattr(self.frame, 'app')
            myapp = self.frame.app()
            print(myapp)
            environ = {}
            environ['PATH'] = request_url
            print(environ['PATH'])
            content = myapp.app(environ,self.set_app_header)
            print(content.decode('utf-8'))


            #self.response_header += '\r\n'
            response_body = content
            client_conn.send(bytes(self.response_header, encoding='gbk'))
            client_conn.send(response_body)
            #self.response_header = ''

        #client_conn.close()

    def set_app_header(self,status_code,headers):
        response_status_code = 'HTTP/1.1 ' + status_code
        self.response_header = response_status_code
        for k,v in headers:
            self.response_header += ('%s:%s\r\n' % (k,v))
        self.response_header += '\r\n'
        print(self.response_header)

        #self.response_header = [status_code,headers]



if __name__ == '__main__':
    my_server = http_server()
    my_server.run_server()
