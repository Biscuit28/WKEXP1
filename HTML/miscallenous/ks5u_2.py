# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, re
from dateformat import format_date
from multiprocessing import Process
from extract_data2 import extraction


class ks5u_2:

    #Adapted from Ks5u_1.py, speed improvements
    #now reads res_province, res_city, res_county
    #last updated, July 20th 2017
    #NOTE this DOES NOT WORK if there are no previous data in database

    def __init__(self, host, port):

        logfile = '/opt/spider/logs/ks5uF.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(host, port)
        self.collection = client.spider.ks5u
        self.start_time = datetime.today()
        self.document_list = []
        self.areas = [u'北京',u'天津',u'上海',u'重庆',u'河北',u'辽宁',u'黑龙江',u'吉林'
        ,u'山东',u'山西',u'安徽',u'浙江',u'江苏',u'江西',u'广东',u'福建',u'海南',u'河南',
        u'湖北',u'湖南',u'四川',u'云南',u'贵州',u'陕西',u'甘肃',u'青海',u'宁夏',u'内蒙古',
        u'广西',u'西藏', u'新疆', u'香港', u'澳门', u'台湾']


    def read_url(self, URL_DATE, URL_NUM):

        target = 'http://www.ks5u.com/down/' + URL_DATE + str(URL_NUM) + '.shtml'
        tries = 0

        while tries < 10:

            try:
                urlobj = urllib2.urlopen(target, timeout=5)
                return(urlobj.geturl(), unicode(urlobj.read(), 'gb18030'))
            except Exception, e:
                print 'URL could not open. trying again'
                print e
                tries += 1

        print 'encountering URL erros, saving our progress'
        self.save_progress()
        self.logging(2)
        quit()


    def get_info(self, html, URL_DATE, res_url, res_id):

        try:

            d = pq(html)

            res_intro = ''
            res_title = d('#w4 h1').text()
            e = d('#w4 .e')
            res_type = e.find('p').eq(0).text().replace(u'资料类别', '').strip()

            res_point = e.find('p').eq(3).text().replace(u'下载扣点', '').strip()
            res_point = re.sub("\D", "", res_point)

            res_downcount = e.find('p').eq(9).text().replace(u'下载统计', '').strip()
            res_version = e.find('p').eq(4).text().replace(u'教材版本', '').strip()
            res_subject = e.find('p').eq(5).text().replace(u'使用学科', '').strip()
            res_class = e.find('p').eq(6).text().replace(u'使用年级', '').strip()
            res_date = format_date(URL_DATE)

            (res_province, res_city, res_county) = extraction(res_title)

            area_list = [x for x in self.areas if x in res_title]
            area_list.append('')
            res_area = area_list[0]

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_area': res_area,
                        'res_stage': u'高中', 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id}

            print res_title, res_date, res_url
            self.document_list.append(document)

        except Exception, e:
            print 'bad html', e


    def collect(self):

        last_saved = self.save_progress(save=False)
        URL_DATE, URL_NUM, BAD_COUNT = last_saved[0], last_saved[1], 0

        while True:

            while BAD_COUNT <= 50:

                URL = 'http://www.ks5u.com/down/' + URL_DATE + str(URL_NUM) + '.shtml'
                DATA = self.read_url(URL_DATE, URL_NUM)
                URL_NUM += 1
                print URL

                if 'http://www.ks5u.com/CreateHtml' in DATA[0]:
                    BAD_COUNT += 1
                    print BAD_COUNT, 'bad url'
                elif URL_DATE not in DATA[0]:
                    print URL_DATE, 'not in ', DATA[0]
                    URL_DATE = self.date_update(DATA[0])
                    BAD_COUNT = 0
                    break
                else:
                    BAD_COUNT = 0
                    break

            if BAD_COUNT > 50:
                URL_NUM = URL_NUM - BAD_COUNT
                print 'Most likely no more data to be read....Terminating.'
                break

            self.get_info(DATA[1], URL_DATE, URL, URL_NUM -1)

        self.save_progress()
        self.logging(1)


    def date_update(self, URL):

        URL = URL[25:]
        URLDATE = URL.split('/')[:-1]
        return URLDATE[0] + '/' + URLDATE[1] + '/'


    def save_progress(self, save=True):

        if save:
            if len(self.document_list) > 0:
                self.collection.insert_many(self.document_list)
        else:
            doc = self.collection.find({}).sort('res_id', -1).limit(1)[0]
            infolist = doc['res_url'].split('/')
            return (infolist[4] +'/'+infolist[5]+'/', int(doc['res_id']) + 1)


    def logging(self, option):

        end = datetime.today()
        if option == 1:
            s = '{}, {} NEW ITEMS FOUND. PROCESSING TIME = {}'.format(end, len(self.document_list), end - self.start_time)
            print s
            logging.info(s)
        if option == 2:
            s = '{}, URL opening issues, terminating program... {} new items fonund, processing time = {}'.format(end, len(self.document_list), end - self.start_time)
            print s
            logging.info(s)



if __name__ == '__main__':
    ks5u = ks5u_2('10.1.1.13', 27017)
    ks5u.collect()
