#!/usr/bin/python3
# -*- coding:utf-8 -*-
#auth:zhiyi
import time
import re
import asyncio
from functools import wraps


def route(url,route_dict):
    def set_func(func):
        route_dict[url] = func
        def call_func(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return call_func
    return set_func

class app(object):
    route_dict = {}
    def __init__(self):
        self.g_templates_dir = './templates'
        self.g_dynamic_dir = './dynamic'
        self.g_static_dir = './static'

        self.content = None
        self.stock_info = '''<td>01</td><td>600028</td><td>中国石化</td><td>-1.15%</td><td>0.16%</td><td>6.02</td><td>6.04</td><td>20170812</td><td></td>'''


    @route('/index.py',route_dict)
    def index(self,template_file):
        with open(template_file,'rb') as f:
            content = f.read()

        content = content.decode('utf-8')
        content = re.sub('\{content\}',self.stock_info,content)
        print(content)
        return content.encode('utf-8')

    @route('/center.py',route_dict)
    def center(self,template_file):
        with open(template_file,'rb') as f:
            content = f.read()
        return content


    def app(self,environ,set_headers):
        try:
            #if environ['PATH_INFO'] in app.route_dict.keys():
                file_name = environ['PATH_INFO']
                print(file_name)
                file_name = file_name.replace('.py','.html')

                file_name = self.g_templates_dir + file_name
                print(file_name)
                #self.content = self.index(file_name)
                func = app.route_dict[environ['PATH_INFO']]
                print(func)
                self.content = func(self,file_name)
                print(self.content)
                #print(self.content)
                header_status = '200 OK\r\n'
                header_body = [('Content-Type','text/html')]
                content_len = len(self.content)
                header_body.append(('Content-Length',content_len))
                #print('-' * 50)
                #print(header_status,header_body)
                #print('-' * 50)
                #print(set_headers)
                set_headers(header_status,header_body)
                return self.content
        except Exception as e:
            with open('./templates/404.html', 'rb') as f:
                content = f.read()
                response_status = '404 Not Found\r\n'
                response_header = [('Content_Length:',len(content))]
                set_headers(response_status, response_header)
            return content + str(e).encode('gbk')





if __name__ == '__main__':
    pass