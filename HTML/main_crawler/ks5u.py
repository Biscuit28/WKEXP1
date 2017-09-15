# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, re, traceback
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class ks5u_2:

    '''
    Ks5u scraper - Urllib2 (Adapted from Ks5u1)
    Last Updated: Wednesday, August 23rd 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/ks5uF.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.current_url = 0
        self.collection = client.spider.ks5u
        self.res_urls = set([])
        self.collection_res = client.spider.res
        self.start_time = datetime.today()
        self.initial = self.collection.count()
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)


    def read_url(self, target, tries=10):

        '''
        Reads html from url and encodes it gb18030. Each url is given 10 tries
        before it is scrapped
        '''

        while tries > 0:
            try:
                urlobj = urllib2.urlopen(target, timeout=5)
                return(urlobj.geturl(), unicode(urlobj.read(), 'gb18030'))
            except Exception, e:
                print e
                tries -= 1
        self.logging(2)
        quit()


    def get_info(self, html, res_url, res_id):

        '''
        Reads all relevant data from selected download page
        '''

        try:
            d = pq(html)
            res_grade = u'高中'
            res_title = d('#w4 h1').text()
            res_intro = d('#Res_Content').text()
            e = d('#w4 .e')
            res_type = e.find('p').eq(0).text().replace(u'资料类别', '').strip()
            res_point = e.find('p').eq(3).text()
            res_point = int(re.sub("\D", "", res_point))
            res_downcount = e.find('p').eq(9).text().replace(u'下载统计', '').strip()
            res_version = e.find('p').eq(4).text().replace(u'教材版本', '').strip()
            res_subject = e.find('p').eq(5).text().replace(u'使用学科', '').strip()
            res_class = e.find('p').eq(6).text().replace(u'使用年级', '').strip()
            res_date = dateformat.format_date(e.find('p').eq(8).text().replace(u'更新时间', '').strip())
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
            crawl_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type,
                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id,
                        'res_file': '', 'site_id': 'ks5u', 'date': crawl_date}

            print res_url, res_date
            if res_url not in self.res_urls:
                self.collection.insert_one(document)
                self.collection_res.insert_one(document)
            else:
                print 'document exists'
        except Exception, e:
            tb = traceback.format_exc()
            logging.info('getting {} failed. Reason: {}'.format(res_url, tb))
            print tb



    def collect(self, range=False):

        '''
        Collects from http://www.ks5u.com/down/DATE/LAST_RES_ID.shtml
        METHOD - Traversal through incrementing res_id

        NEW - optional range arugment is a list [a,b] where documents are retrieved
        from the a to b non-inclusive, ie a=2, b=5, the range is (2,3,4)
        '''

        if not range:
            if self.initial == 0:
                self.get_info(self.read_url('2017-7/1/', 2773821)[1], 'http://www.ks5u.com/down/2017-7/1/2773821.shtml')
            doc = self.collection.find({}).sort('res_id', -1).limit(1)[0]
            main_url = doc['res_url'][:-(len(str(r_id))+6)]
            r_id = doc['res_id']
            max_id = float('inf')
        else:
            self.res_urls = set(self.collection.distinct('res_url'))
            r_id = range[0] - 1
            max_id = range[1]
            main_url = 'http://www.ks5u.com/down/2017-8/4/' #/2017-8/4/ could be any valid date theoretically

        print 'starting at ', r_id + 1

        while True:
            BAD_COUNT = 0
            while BAD_COUNT <= 50:
                r_id += 1
                URL = main_url + str(r_id) + '.shtml'
                self.current_url = r_id
                DATA = self.read_url(URL)
                if 'http://www.ks5u.com/CreateHtml' in DATA[0]:
                    BAD_COUNT += 1
                    print BAD_COUNT, 'bad url'
                else:
                    main_url = DATA[0][:-(len(str(r_id))+6)]
                    break
            if BAD_COUNT > 50 or r_id >= max_id+1:
                break
            self.get_info(DATA[1], URL, r_id)
        self.logging(1)


    def logging(self, option):

        '''
        Takes care of all logging.
        option = 1 - > program exit correctly
        otion = 2 -> program exits incorrectly (unable to open url)
        '''

        end = datetime.today()
        if option == 1:
            s = '{}, {} NEW ITEMS ADDED. PROCESSING TIME = {}'.format(end, self.collection.count() - self.initial, end - self.start_time)
        if option == 2:
            s = '{}, URL opening issues at {}, terminating program... {} new items fonund, processing time = {}'.format(end, self.current_url, self.collection.count() - self.initial, end - self.start_time)
        logging.info(s)
        print s


if __name__ == '__main__':
    ks5u = ks5u_2()
    ks5u.collect()
    #ks5u.collect([2499395, 2772772])  # 2479110 -> 2017 01 01 1st doucment, 2499395
