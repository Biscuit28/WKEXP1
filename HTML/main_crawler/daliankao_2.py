# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, traceback
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class daliankao_2:

    '''
    Daliakao scraper - Urllib2
    Last Updated: Wednesday, Augst 23rd 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/daliankaoF.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.current_url = 0
        self.type_dict = {}
        self.collection = client.spider.daliankao
        self.collection_res = client.spider.res
        self.res_urls = set(self.collection.distinct('res_url'))
        self.start_time = datetime.today()
        self.initial = self.collection.count()
        self.subject_set = set([x['name'] for x in client.config.subject.find()])
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        for types in client.config.restypes.find():
            self.type_dict[types['xkw_type']] = set(types['daliankao_type'].split())


    def read_url(self, res_id, tries=10):

        '''
        Reads html from url. Each url is given 10 tries before it is scrapped
        '''

        target = 'http://www.daliankao.org/down/' + str(res_id) + '.html'
        while tries > 0:
            try:
                html = urllib2.urlopen(target, timeout=5).read()
                if '404 - 没有找到您要访问的页面' in html:
                    return False
                else:
                    return html
            except Exception, e:
                print 'URL could not open. trying again', e
                tries -= 1
        self.logging(2)
        quit()


    def collect(self, range=False):

        '''
        Collects from 'http://www.daliankao.org/down/LATEST_RES_ID.html
        METHOD - Traversal through incrementing res_id

        NEW - optional range arugment is a list [a,b] where documents are retrieved
        from the a to b non-inclusive, ie if  a=2, b=5, the range is (2,3,4)
        '''

        if not range:
            if self.initial == 0:
                self.get_info(1171458, self.read_url(1171458))
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
            res_intro, res_type, res_grade, res_class = '', '', '', ''
            res_title = d('h3.paper-title').text()
            table = d('div.c').find('p')
            res_point = float(table.eq(7).find('span a').text())
            res_version = table.eq(1).find('span').text()
            res_downcount = int(table.eq(4).find('span').text()[:-1])
            res_date = dateformat.format_date(table.eq(3).find('span').text())
            res_type_o = table.eq(5).find('span').text()
            for k in self.type_dict.keys():
                if res_type_o in self.type_dict[k]:
                    res_type = k
                    break
            rs_1 = table.eq(0).find('span a').eq(0).text()
            rs_2 = table.eq(0).find('span a').eq(1).text()
            if rs_1 in self.subject_set:
                res_subject = rs_1
            elif rs_2 in self.subject_set:
                res_subject = rs_2
            else:
                res_subject = ''
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
            res_url = 'http://www.daliankao.org/down/' + str(res_id) + '.html'
            crawl_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_type_o': res_type_o,
                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id,
                        'res_file': '', 'site_id': 'daliankao', 'date': crawl_date}

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
            s = '{}, URL opening issues at {}, terminating program... {} new items fonund, processing time = {}'.format(end, self.current_url, self.collection.count() - self.initial, end - self.start_time)
        logging.info(s)
        print s




if __name__ == "__main__":
    daliankao = daliankao_2()
    daliankao.collect()
    #daliankao.collect([1116308, float('inf')]) #http://www.daliankao.org/down/1112055.html 2017-01-12 00:00:00, 1116308
