# -*- coding: UTF-8 -*-

import re, urllib, urllib2, os, sys, threading, time, pymongo, logging, platform
from pyquery import PyQuery as pq
from multiprocessing import Process
from urllib2 import Request, urlopen, URLError, HTTPError
from datetime import *
if platform.system() == 'Linux':
    sys.path.append('/opt/git/Spider/src/')
if platform.system() == 'Windows':
    sys.path.append('../')
from data import conf

#i guess we can divide the process into chunks
#the speed problem is because the url is not complete
#if the url is full, it loads at a much faster pace

class KS5U_1:

    def __init__(self):
        logfile = '/opt/spider/logs/ks5u_1.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        db = client['spider']
        self.table = db.ks5u
        self.site = 'http://www.ks5u.com'
        self.cache = []

    # 更新详情
    def get_detail(self, ks5u_id, url):
        '''
        extracts all the information from the webpage (from the given url)

        CALLED BY get_list
        '''
        areas = [u'北京',u'天津',u'上海',u'重庆',u'河北',u'辽宁',u'黑龙江',u'吉林',u'山东',u'山西',u'安徽',u'浙江',u'江苏',u'江西',u'广东',u'福建',u'海南',u'河南',u'湖北',u'湖南',u'四川',u'云南',u'贵州',u'陕西',u'甘肃',u'青海',u'宁夏',u'内蒙古',u'广西',u'西藏', u'新疆', u'香港', u'澳门', u'台湾']
        #open url
        html = urllib2.urlopen(url).read()
        print 'open', url
        #print html
        try:
            text = unicode(html, "gbk")
            if text != '':
                d = pq(text)
                # 标题
                title = d('#w4 h1').text()
                e = d('#w4 .e')
                # 类型
                s_type = e.find('p').eq(0).text().replace(u'资料类别', '').strip()
                # 点数
                s_point = e.find('p').eq(3).text().replace(u'下载扣点', '').strip()
                s_point = re.sub("\D", "", s_point)
                # 下载量
                s_downcount = e.find('p').eq(9).text().replace(u'下载统计', '').strip()
                # 教材版本
                s_version = e.find('p').eq(4).text().replace(u'教材版本', '').strip()
                # 学科
                s_subject = e.find('p').eq(5).text().replace(u'使用学科', '').strip()
                # 年级
                s_class = e.find('p').eq(6).text().replace(u'使用年级', '').strip()
                # 资料上传的时间
                s_date = e.find('p').eq(8).text().replace(u'更新时间', '').strip()
                # 所属区域
                area_list = [x for x in areas if x in title]
                area_list.append('')
                s_area = area_list[0]
                # 简介
                s_intro = ''
                #print url, title, s_type, s_point, s_version, s_subject, s_class, s_date, s_area
                if title != '':
                    print title
                q = {
                    'res_url':      url,
                    'res_title':    title
                }
                o = {
                    'res_id':       ks5u_id,
                    'res_url':      url,
                    'res_title':    title,
                    'res_type':     s_type,
                    'res_version':  s_version,
                    'res_subject':  s_subject,
                    'res_class':    s_class,
                    'res_date':     s_date,
                    'res_area':     s_area,
                    'res_intro':    s_intro,
                    'res_downcount':s_downcount,
                    'res_point':    s_point
                }
                if (self.table.find(q).count() == 0) and (title != ''):
                    self.table.save(o)
                    print 'save', o['res_url']
                    self.count += 1
                if title == '':
                    self.nothing_count += 1
                else:
                    self.nothing_count = 0                  #the moment we find an occurence where title exists it resets the counter?
                if self.nothing_count > 200:
                    print 'nothing_count:', self.nothing_count
                    self.over = True
        except BaseException, e:
            print e.message
            logging.info('%s %s' % (datetime.today(), e.message))
            self.over = True


    def get_list(self, my_ks5u_id=0):
        self.nothing_count = 0
        self.count = 0
        self.over = False
        starttime = datetime.now()
        data = self.table.find({}).sort('res_id', -1).limit(1)
        ks5u_id = data[0]['res_id']
        if my_ks5u_id != 0: #condition when we want to read from a custom level. otherwise from where we left off
            ks5u_id = my_ks5u_id
        while self.over == False:
            self.get_detail(ks5u_id, 'http://www.ks5u.com/down/%d.shtml' % ks5u_id)
            if self.over == False:
                ks5u_id += 1
        endtime = datetime.now()
        times = (endtime - starttime).seconds
        s = '%s update %d (%ds)' % (datetime.today(), self.count, times)
        print(s)
        logging.info(s)

#2773821

if __name__ == '__main__':
    if len(sys.argv) == 1:
        ks5u = KS5U_1()
        ks5u.get_list()
    if len(sys.argv) == 2:
        ks5u = KS5U_1()
        ks5u.get_list(int(sys.argv[1]))
