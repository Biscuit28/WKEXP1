# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import urllib2, pymongo, logging, time, sys, traceback
from multiprocessing import Process
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class dearedu:

    '''
    Dearedu scraper - Urllib2
    Last Updated: Thursday, August 10th 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/dearedu.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        init = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        initialize_versions = init.config.version
        initialize_subjects = init.config.subject
        versions = initialize_versions.find_one({"dearedu" : {"$exists": 1}})['dearedu']
        init.close()

        self.G_VERSION = set([i for i in versions['highschool'].split()])
        self.C_VERSION = set([j for j in versions['juniorhigh'].split()])
        self.X_VERSION = set([k for k in versions['elementary'].split()])
        self.subject_set = set([l['name'] for l in initialize_subjects.find({})])
        self.type_set = set([u'试题', u'教案', u'课件', u'学案', u'素材', u'论文', u'教学案'])
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()


    def read_url(self, target):

        '''
        Reads html from webpage. Dearedu does not need encoding
        '''

        return urllib2.urlopen(target, timeout=30).read()


    def execute(self, grades):

        '''
        Reads all relevant data from a given document list.
        Each process is tasked with a grade
        '''

        document_list = []
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collection = client.spider.dearedu
        collection_res = client.spider.res
        res_intro, res_downcount = '',''
        res_grade = grades.text()
        grade_url = grades.find('a').attr('href')
        PAGE_COUNT = 1
        EXIT = False
        while PAGE_COUNT <= 100:
            page_extension = '&p='+str(PAGE_COUNT)
            pq_page = pq(self.read_url(grade_url + page_extension))
            for i in range(0, 10):
                try:
                    articles = pq_page('.z_right .lb_zs .lb_grey .lb_aload .lb_bleft').eq(i)
                    tmp = articles('span').text()
                    order_text = tmp[4:]
                    res_title = articles('h1').find('a').text()
                    res_url =   articles('h1').find('a').attr('href')
                    date =  articles('p').eq(0).text()
                    area =  articles('p').eq(1).text()
                    point = articles('p').eq(3).text()
                    res_date = dateformat.format_date(date[3:])
                    res_area = area[3:]
                    res_point = point[3:]
                    if res_point != u'免费':
                        res_point = int(res_point)
                    (res_subject, res_type, res_class) = self.extract_info(order_text)
                    res_id = int(filter(str.isdigit, str(res_url)))
                    (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
                    (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
                    res_version = self.res_version(res_title, res_grade)

                    document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                                'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_area': res_area,
                                'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                                'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_file': '', 'site_id': 'dearedu',
                                'res_id': res_id}

                    print res_url, res_date
                    if self.check_date(res_date, datetime.today()):
                        print 'document too old'
                        EXIT = True
                        break
                    if collection.find_one({'res_url': res_url}):
                        EXIT = True
                        print 'document already exists'
                        break
                    document_list.append(document)
                except Exception:
                    traceback.print_exc()
            if EXIT:
                break
            PAGE_COUNT += 1
        if len(document_list) > 0:
            collection.insert_many(document_list)
            collection_res.insert_many(document_list)
        client.close()


    def collect(self):

        '''
        Collects from http://s.dearedu.com/list.php?g=1&
        METHOD - traversal through tabs, multiprocessing
        '''

        start_time = datetime.today()
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collection = client.spider.dearedu
        start_count = collection.count()
        pq_main = pq(self.read_url('http://s.dearedu.com/list.php?g=1&'))
        processes = []
        for grades in pq_main('.hide666 dl dt').items():
            p = Process(target = self.execute, args = (grades,))
            p.start()
            processes.append(p)
        for j in processes:
            j.join()
        end_count = collection.count()
        end_time = datetime.today()
        s = '{}, {} NEW ITEMS FOUND. PROCESSING TIME = {}'.format(end_time, end_count - start_count, end_time - start_time)
        print s
        logging.info(s)


    def extract_info(self, info_string):

        '''
        Method is specific to Dearedu only. Sorts and finds res_subject,
        res_type, and res_class from a info string in every document list
        '''

        arr = info_string.split('>')
        res_class = arr[0]
        type_list = []
        res_subject = ''
        for e in arr:
            e = e.strip()
            if e in self.subject_set:
                res_subject = e
            if e in self.type_set:
                if e == u'教学案':
                    type_list.append('学案')
                type_list.append(e)
        if len(type_list) != 1:
            res_type = ''
        else:
            res_type = type_list[0]
        res_class = res_class.strip()
        return (res_subject, res_type, res_class)


    def res_version(self, title, grade):

        '''
        Find version if version in our database can be found in document title
        '''

        res_version = ''
        if grade == u"高中":
            word_set = self.G_VERSION
        if grade == u"初中":
            word_set = self.C_VERSION
        if grade == u"小学":
            word_set = self.X_VERSION
        title = title.upper()
        for w in word_set:
            w = w.upper()
            if w in title:
                res_version += w + ' '
        res_version = res_version.strip()
        return res_version


    def check_date(self, res_date, res_today):

        '''
        If document is older than current Month, deem it as too old to scrape.
        '''

        res_today = res_today.strftime('%Y-%m-%d')
        res_date = res_date.split('-')
        res_today = res_today.split('-')
        return  ((int(res_date[0])==int(res_today[0])) and (int(res_date[1]) < int(res_today[1]))) or (int(res_date[0])<int(res_today[0]))




if __name__ == '__main__':

    dearedu = dearedu()
    dearedu.collect()
