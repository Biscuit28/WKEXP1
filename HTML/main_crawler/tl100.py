# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, traceback
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class tl100:

    '''
    Tl100 scraper - Urllib2
    Last Updated: Wednesday, August 23rd 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/tl100.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.current_url = 0
        self.collection = client.spider.tl100
        self.collection_res = client.spider.res
        self.res_urls = set(self.collection.distinct('res_url'))
        self.start_time = datetime.today()
        self.initial = self.collection.count()
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)


    def read_url(self, res_id, tries=10):

        '''
        Reads html from url. Each url is given 10 tries before it is scrapped
        '''

        target = 'http://taoti.tl100.com/detail-' + str(res_id) + '.html'
        while tries > 0:
            try:
                return urllib2.urlopen(target, timeout=5).read()
            except urllib2.HTTPError, e:
                if e.code == 404:
                    return False
                else:
                    tries -= 1
            except Exception, e:
                print e
                tries -= 1
        self.logging(2)
        quit()


    def collect(self, range=False):

        '''
        Collects from http://taoti.tl100.com/detail-LATEST_RES_ID.html
        METHOD - Traversal through incrementing res_id

        NEW - optional range arugment is a list [a,b] where documents are retrieved
        from the a to b non-inclusive, ie if  a=2, b=5, the range is (2,3,4)
        '''

        if not range:
            if self.initial == 0:
                self.get_info(888416, self.read_url(888416))
            doc = self.collection.find({}).sort('res_id', -1).limit(1)[0]
            r_id = doc['res_id']
            max_id = float('inf')
        else:
            r_id = range[0] - 1
            max_id = range[1]

        print 'starting at ', r_id + 1

        while True:
            BAD_COUNT = 0
            while BAD_COUNT <= 50:
                r_id += 1
                self.current_url = r_id
                DATA = self.read_url(r_id)
                if not DATA:
                    BAD_COUNT += 1
                    print 'bad url', BAD_COUNT
                else:
                    break
            if BAD_COUNT > 50 or r_id >= max_id+1:
                self.logging(1)
                quit()
            self.get_info(r_id, DATA)
        self.logging(1)


    def get_info(self, res_id, DATA):

        '''
        Reads all relevant data from selected download page
        '''

        try:
            d = pq(DATA)
            res_grade = '', ''
            res_title = d('div.nexttopR_head h1.ell').text()
            res_url = 'http://taoti.tl100.com/detail-' + str(res_id) + '.html'
            res_point = int(d('#point strong').text())
            table1 = d('#sx tr')
            res_class = table1('td').eq(1).text()
            res_intro = d('div.contentbox table td p').text()
            res_subject = table1('td').eq(3).text()
            res_version = table1('td').eq(5).text()
            res_type = table1('td').eq(7).text()
            table2 = d('div.title2 tr td').eq(0).text().split('|')
            res_date = dateformat.format_date(table2[1][6:])
            rp = table2[2][5:]
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class,)
            res_province = rp
            res_downcount = int(d('#hits').text())
            crawl_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type,
                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id,
                        'res_file': '', 'site_id': 'tl100', 'date': crawl_date}

            print res_url, res_date
            if res_url not in self.res_urls:
                self.collection.insert_one(document)
                self.collection_res.insert_one(document)
            else:
                print 'document exists'
        except Exception:
            tb = traceback.format_exc()
            logging.info('getting {} failed. Reason: {}'.format(res_id, tb))
            print tb


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
            s = '{}, URL opening issues at {}, terminating program... {} new items found, processing time = {}'.format(end, self.current_url, self.collection.count() - self.initial, end - self.start_time)
        print s
        logging.info(s)



if __name__ == "__main__":
    tl100 = tl100()
    tl100.collect()
    #tl100.collect([863026, float('inf')])

    # client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
    # collection = client.spider.tl100
    # collection_res = client.spider.res
    # for d in collection.find({'res_intro': ''}):
    #     res_intro = ''
    #     _id = d['_id']
    #     url = d['res_url']
    #     try:
    #         find = pq(unicode(urllib2.urlopen(url).read(), 'gb18030'))
    #         res_intro = find('div.contentbox table td p').text()
    #         if res_intro == '':
    #             print 'nothing found m8'
    #     except Exception:
    #         traceback.print_exc()
    #     print '------------'
    #     print url
    #     print res_intro
    #     print '------------'
    #     collection.update({'_id': _id}, {"$set": {'res_intro': res_intro}}, upsert=False)
    #     collection_res.update({'res_url': url}, {'$set': {'res_intro': res_intro}}, upsert=False)
