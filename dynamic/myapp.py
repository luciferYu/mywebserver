#!/usr/bin/python3
# -*- coding:utf-8 -*-
#auth:zhiyi
import time
import re
import pymysql
import urllib.parse
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
        #self.stock_info = '''<td>01</td><td>600028</td><td>中国石化</td><td>-1.15%</td><td>0.16%</td><td>6.02</td><td>6.04</td><td>20170812</td><td></td>'''

        #self.stock_info_list = ['01','600028','中国石化','-1.15%','0.16%','6.02','6.04','20170812','']
        self.conn = pymysql.connect(host='localhost', user='yuzhiyi', password='abc123,', db='stock_db', charset='utf8')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    @route(r'/add/(\d+)\.html',route_dict)
    def add(self,template_file):
        stock_code = ''
        print(template_file)
        code = re.match(r'./templates/add/(\d+)\.html',template_file).group(1)
        #print(code)
        self.cur.execute('select info.id from focus,info where focus.info_id = info.id and info.code = %s;',code)
        ret = self.cur.fetchone()
        if not ret:
            self.cur.execute('insert into focus(info_id) select id from info where code=%s ',code)
            self.conn.commit()
            return '关注成功'.encode('utf-8')
        else:
            return '请不要重复关注'.encode('utf-8')

    @route(r'/del/(\d+)\.html', route_dict)
    def add(self, template_file):
        stock_code = ''
        print(template_file)
        code = re.match(r'./templates/del/(\d+)\.html', template_file).group(1)
        # print(code)
        self.cur.execute('delete from focus where focus.info_id = (select id from info where code=%s );', code)
        self.conn.commit()
        return '删除成功'.encode('utf-8')

    @route(r'/update/(\d+)/(.*?)\.html', route_dict)
    def update_note_info(self, template_file):
        stock_code = ''
        print(template_file)
        code = re.match(r'./templates/update/(\d+)/(.*?)\.html', template_file).group(1)
        note_info = re.match(r'./templates/update/(\d+)/(.*?)\.html', template_file).group(2)
        note_info_new = urllib.parse.unquote(note_info)
        # print(code)
        self.cur.execute('update focus set note_info=%s where focus.info_id = (select id from info where code=%s );', (note_info_new,code))
        self.conn.commit()
        return '更新成功'.encode('utf-8')


    @route(r'/index.html',route_dict)
    def index(self,template_file):
        with open(template_file,'rb') as f:
            content = f.read()

        content = content.decode('utf-8')
        data = self.get_index_data_from_db()
        data = sorted(data,key=lambda x:x[0])

        page_data = self.add_index_page(len(data))


        self.stock_info = self.deal_with_data(data[0:10])

        content = re.sub('\{%content%\}',self.stock_info,content)
        content = re.sub('\{%page%\}',page_data,content)
        #print(content)
        return content.encode('utf-8')

    @route(r'/index/(\d+)\.html', route_dict)
    def index(self, template_file):
        with open('./templates/index.html', 'rb') as f:
            content = f.read()
        page = re.match(r'./templates/index/(\d+)\.html', template_file).group(1)
        content = content.decode('utf-8')
        data = self.get_index_data_from_db()
        data = sorted(data, key=lambda x: x[0])

        page_data = self.add_index_page(len(data))
        start_page = int(page)*10 -10
        end_page = int(page)*10
        self.stock_info = self.deal_with_data(data[start_page:end_page])

        content = re.sub('\{%content%\}', self.stock_info, content)
        content = re.sub('\{%page%\}', page_data, content)
        # print(content)
        return content.encode('utf-8')

    @route(r'/center.html',route_dict)
    def center(self,template_file):
        with open(template_file,'rb') as f:
            content = f.read()

        content = content.decode('utf-8')
        data = self.get_center_data_from_db()
        data = self.deal_center_with_data(data)
        #print(data)
        content = re.sub('\{%content%\}',data, content)


        return content.encode('utf-8')

    @route(r'/update/(\d+)\.html', route_dict)
    def update(self, template_file):
        with open('./templates/update.html', 'rb') as f:
            content = f.read()

        content = content.decode('utf-8')
        code = re.match(r'./templates/update/(\d+)\.html', template_file).group(1)
        self.cur.execute('select focus.note_info from focus,info where focus.info_id = info.id and info.code = %s;',code)
        note_info = self.cur.fetchone()[0]
        note_info_new = urllib.parse.unquote(note_info)
        #data = self.deal_center_with_data(data)
        # print(data)
        #content = re.sub('\{%content%\}', data, content)
        content = re.sub('\{%code%\}',code, content)
        content = re.sub('\{%note_info%\}', note_info, content)
        return content.encode('utf-8')

    def app(self,environ,set_headers):
        try:
            #if environ['PATH_INFO'] in app.route_dict.keys():
                file_name = environ['PATH_INFO']
                print(file_name)
                #file_name = file_name.replace('.py','.html')



                for k,v in app.route_dict.items():
                    print('print k v ',k,v)
                    ret = re.match(k,file_name)
                    print('print ret',ret)
                    if ret:
                        print('in if')
                        file_name = self.g_templates_dir + file_name
                        self.content =  v(self,file_name)
                        print(self.content)
                        break
                    else:
                        pass
                #self.content = self.index(file_name)
                #func = app.route_dict[environ['PATH_INFO']]
                #print(func)
                #print(file_name)
                #self.content = func(self,file_name)
                #print(self.content)
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

    def get_index_data_from_db(self):
        self.cur.execute('select * from info')
        stock_info = self.cur.fetchall()
        #for info in stock_info:
            #print(info)
        return stock_info

    def get_center_data_from_db(self):
        self.cur.execute('select info.code,info.short,info.chg,info.turnover,info.price,info.highs,focus.note_info from focus INNER JOIN info on focus.info_id = info.id;')
        focus_info = self.cur.fetchall()
        #for info in stock_info:
            #print(info)
        return focus_info

    def deal_with_data(self,data):
        format_data = ''
        for stock in data:
            tmp_row_data = ''
            for i,field in enumerate(stock):
                if i in (3,4):
                    tmp_row_data += self.add_color_td(field)
                else:
                    tmp_row_data += self.add_td(field)
            tmp_row_data += '''<td><input type='button' value='添加自选' id="toAdd" name="toAdd" systemidvaule="%s"></td>''' % stock[1]
            format_data += self.add_tr(tmp_row_data)
        return format_data

    def deal_center_with_data(self,data):
        format_data = ''
        for stock in data:
            tmp_row_data = ''
            for field in stock:
                if str(field).endswith('%'):
                    tmp_row_data += self.add_color_td(field)
                else:
                    tmp_row_data += self.add_td(field)
            s ='''
            <td><a type = "button" class ="btn btn-default btn-xs" href="/update/%s.html"><span class ="glyphicon glyphicon-star" aria-hidden="true"></span>修改</a></td>
            <td><input type = "button" value = "删除" id="toDel" name="toDel" systemidvaule="%s"></td>
            ''' % (stock[0],stock[0])
            print(s)
            tmp_row_data += s
            format_data += self.add_tr(tmp_row_data)
        return format_data

    def add_color_td(self,string):
        if float(string[:-1]) > 0:
            tmp_string = '%s' % string
            return '<td style="color:red;">' + tmp_string + "</td>"
        elif float(string[:-1]) < 0:
            tmp_string = '%s' % string
            return '<td style="color:green;">' + tmp_string + "</td>"

    def add_td(self,string):
        tmp_string = '%s' % string
        return '<td>' + tmp_string + '</td>'

    def add_tr(self,string):
        return '<tr>' + string + '</tr>'

    def add_index_page(self,len):
        pages = ''
        for i in range((len//10 +1)):
            s = '''<a href=/index/%s.html> 第%d页 </a>''' % (i+1,i+1)
            pages += s
        return pages



if __name__ == '__main__':
    a = app()
    data = a.get_index_data_from_db()
    stock_info = a.deal_with_data(data)
    print(stock_info)

