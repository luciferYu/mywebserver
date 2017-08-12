#!/usr/bin/python3
# -*- coding:utf-8 -*-
#auth:zhiyi
import time

def response_time(set_app_header,request):
    headers = []
    header_status = '200 OK\r\n'
    header_body = [('Content-type:text/html\r\n')]
    headers = [header_status,header_body]
    print(headers)
    set_app_header(headers)
    return '现在的时间是 %s' % time.time()




if __name__ == '__main__':
    pass