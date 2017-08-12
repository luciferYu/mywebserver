#!/usr/bin/python3
# -*- coding:utf-8 -*-
#auth:zhiyi
import time

class app(object):
    def __init__(self):
        self.g_templates_dir = './templates'
        self.g_dynamic_dir = './dynamic'
        self.g_static_dir = './static'

        self.content = None

    def index(self,template_file):
        with open(template_file,'rb') as f:
            content = f.read()
        return content

    def center(self,template_file):
        with open(template_file,'rb') as f:
            content = f.read()
        return content


    def app(self,environ,set_headers):
        attr = environ['PATH_INFO'].replace('.py','')
        if hasattr(app,attr[1:]):
            file_name = self.g_templates_dir + attr + '.html'
            print(file_name)
            #self.content = self.index(file_name)
            func = getattr(app,attr[1:])
            print(func)
            self.content = func(self,file_name)
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




if __name__ == '__main__':
    pass