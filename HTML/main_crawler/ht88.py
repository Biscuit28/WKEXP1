# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, traceback
from multiprocessing import Process
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class HT88:

    '''
    HT88 scraper - Urllib2/Selenium webdriver
    Last Updated: Thursday, August 10th 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/ht88.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        self.subject_dict = {'语文': 'http://www.ht88.com', '数学': 'http://shuxue.ht88.com' , '英语': 'http://yingyu.ht88.com',
                            '物理': 'http://wuli.ht88.com', '化学': 'http://huaxue.ht88.com', '生物': 'http://shengwu.ht88.com',
                            '历史': 'http://lishi.ht88.com', '地理': 'http://dili.ht88.com', '政治': 'http://zhengzhi.ht88.com'}
        self.client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        self.res_urls = set(self.client.spider.ht88.distinct('res_url'))
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)


    def read_url(self, target, encoding):

        '''
        Reads html from webpage. Encoding used is gbk
        '''

        return unicode(urllib2.urlopen(target, timeout=30).read(), encoding)


    def execute(self, target):

        '''
        Reads all relevant data from a given document list.
        Each process is taksed with a subject
        '''

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collection = client.spider.ht88
        collection_res = client.spider.res
        document_list = []
        p1 = pq(self.read_url(self.subject_dict[target], 'gbk'))
        res_downcount, res_area, res_intro, res_subject = '','','',target

        for i in range(2,10):
            txt = p1('#sub2 ul li').eq(i).find('a').text()
            url_extend = p1('#sub2 ul li').eq(i).find('a').attr('href')
            res_type = txt[2:]
            res_grade, res_class = '', ''
            MAXPAGE = 1
            EXIT = False
            while MAXPAGE <= 6:
                try:
                    p2 = pq(self.read_url(self.subject_dict[target] + url_extend[:-6] + str(MAXPAGE) + '.html', 'gbk'))
                except urllib2.URLError, e:
                    traceback.print_exc()
                C_AMNT = int(p2('form font').eq(1).text())
                for k in range(0, (C_AMNT * 8)-1 , 8):
                    try:
                        TITLE = p2('#content_right .float_left.w_1 .sublist .softlist ul li').eq(k + 4).find('a')
                        res_title = TITLE.text()
                        res_url = self.subject_dict[target] + TITLE.attr('href')[2:]
                        res_date = dateformat.format_date(p2('#content_right .float_left.w_1 .sublist .softlist ul li').eq(k + 3).text())
                        res_version = p2('#content_right .float_left.w_1 .sublist .softlist ul li').eq(k + 6).remove('span').text()
                        data = p2('#content_right .float_left.w_1 .sublist .softlist ul li').eq(k + 5).remove('span').text()
                        (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
                        (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
                        res_id = res_url[7:-5].split('/')[-1]

                        document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                                    'res_point': '', 'res_subject': res_subject, 'res_type': res_type, 'res_area': res_area,
                                    'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                                    'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_file': '',
                                    'res_id': int(res_id), 'site_id': 'ht88'}

                        print res_url, res_date
                        if self.check_date(res_date, datetime.today()):
                            print 'document too old'
                            EXIT = True
                            break
                        if res_url in self.res_urls: # If we find an existing article, we break, pop the one that is a re-occurence, and go to
                            EXIT = True
                            print 'document already exists'
                            break
                        self.res_urls.add(res_url)
                        document_list.append(document)
                    except Exception:
                        tb = traceback.format_exc()
                        logging.info('{}, reason {}'.format(res_url, tb))
                if EXIT:
                    break
                MAXPAGE += 1
        if len(document_list) > 0:
            collection.insert_many(document_list)
            collection_res.insert_many(document_list)
        client.close()


    def collect(self):

        '''
        Collects from http://YOURSUBJECT.ht88.com
        METHOD - traversal through tabs, multiprocessing
        '''

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collection = client.spider.ht88
        start_time = datetime.today()
        start_count = collection.count()
        processes = []
        client.close()
        for task in self.subject_dict.keys():
            p = Process(target = self.execute, args = (task,))
            p.start()
            processes.append(p)
        for j in processes:
            j.join()
        end_count = collection.count()
        end_time = datetime.today()
        s = '{}, {} NEW ITEMS FOUND. PROCESSING TIME = {}'.format(end_time, end_count - start_count, end_time - start_time)
        print s
        logging.info(s)


    def check_date(self, res_date, res_today):

        '''
        If document is older than current Month, deem it as too old to scrape.
        '''

        res_today = res_today.strftime('%Y-%m-%d')
        res_date = res_date.split('-')
        res_today = res_today.split('-')
        return  ((int(res_date[0])==int(res_today[0])) and (int(res_date[1]) < int(res_today[1]))) or (int(res_date[0])<int(res_today[0]))


    def get_remaining_data(self):

        '''
        Specific to HT88, uses selenium webdriver to get missing data such as res_point and
        res_intro
        '''

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collection = client.spider.ht88
        collection_res = client.spider.res
        for doc in collection.find({"$or": [{'res_point': ''}, {'res_intro': ''}]}): #implies we have the newest ones
            try:
                _id = doc["_id"]
                s = doc["res_url"]
                res_intro = doc["res_intro"]
                res_point = doc["res_point"]
                if res_intro == "":
                    try:
                        find = pq(unicode(urllib2.urlopen(s).read(), 'gb18030'))
                        res_intro = find('#description dd').text()
                    except Exception:
                        print s
                        traceback.print_exc()
                    doc["res_intro"] = res_intro
                    print 'res_intro found'
                if res_point == "":
                    r = s[7:].split('/')
                    main = 'http://'+r[0]
                    r_digit = int(filter(str.isdigit, str(r[2])))
                    full = str(main) + '/user/ViewdownHits.asp?ID=' + str(r_digit)
                    find = pq(urllib2.urlopen(full).read())
                    d = find('body').text()
                    dd = d.split(';')
                    try:
                        res_point = int(filter(str.isdigit, str(dd[-2])))
                    except Exception, e:
                        continue
                        print res_point
                    doc["res_point"] = res_point
                collection.update({'_id': _id}, {"$set": doc}, upsert=False)
                collection_res.update({'res_url': s}, {"$set": {'res_intro': res_intro}}, upsert=False)
                collection_res.update({'res_url': s}, {"$set": {'res_point': res_point}}, upsert=False)
            except Exception, e:
                traceback.print_exc()




if __name__ == '__main__':

    ht88 = HT88()
    ht88.collect()
    ht88.get_remaining_data()
