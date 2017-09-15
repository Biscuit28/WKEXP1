# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, traceback
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr

class zxxk:

    '''
    Zxxk scraper - Urllib2
    Last Updated: Thursday, August 10th 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/zxxk.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)
        self.collection = client.spider.zxxk
        self.collection_res = client.spider.res
        self.start_time = datetime.today()
        self.initial = self.collection.count()
        self.subjects = set([sub['name'] for sub in client.config.subject.find()])
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()


    def read_url(self, res_id, tries=10):

        '''
        Reads html from url. Each url is given 10 tries before it is scrapped
        '''

        target = 'http://www.zxxk.com/soft/' + str(res_id) + '.html'
        while tries > 0:
            try:
                urlopen = urllib2.urlopen(target, timeout=5)
                if '404' in urlopen.geturl():
                    return False
                return unicode(urlopen.read(), 'utf-8')
            except Exception:
                traceback.print_exc()
                tries -= 1
        self.logging(2)
        quit()


    def collect(self):

        '''
        Collects from http://www.zxxk.com/soft/LATEST_RES_ID.html
        METHOD - Traversal through incrementing res_id
        '''

        if self.initial == 0:
            self.get_info(6470500, self.read_url(6470500))  #set your initial value
        doc = self.collection.find({}).sort('res_id', -1).limit(1)[0]
        r_id = doc['res_id'] + 1
        print 'starting at ', r_id

        while True:
            BAD_COUNT = 0
            while BAD_COUNT <= 100:
                DATA = self.read_url(r_id)
                r_id += 1
                if not DATA:
                    BAD_COUNT += 1
                    print 'bad url', BAD_COUNT
                else:
                    break
            if BAD_COUNT > 100:
                self.logging(1)
                quit()
            self.get_info(r_id-1, DATA)
        self.logging(1)


    def get_info(self, res_id, DATA):

        '''
        Reads all relevant data from selected download page
        '''

        try:
            d = pq(DATA)
            res_intro, res_grade, res_point, res_subject, res_version, res_class = '', '', '', '', '', ''
            res_title = d('title').text()
            res_date = dateformat.format_date(d('div.time.des').text())
            res_downcount = int(d('div.down.des').text())
            res_intro = d('div.intro-text').text()
            for ele in d('div.res-link a'):
                w = ele.text
                (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, w)
                for j in self.subjects:
                    if j in w:
                        res_subject = j
            res_type = d('div.type a').eq(0).text().strip()
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            res_province = d('div.address.des').text()
            res_url = 'http://www.zxxk.com/soft/' + str(res_id) + '.html'

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type,
                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id,
                        'res_file': '', 'site_id': 'zxxk'}

            print res_url, res_date
            self.collection.insert_one(document)
            self.collection_res.insert_one(document)
        except Exception:
            traceback.print_exc()


    def logging(self, option):

        '''
        Takes care of all logging.
        option = 1 - > program exit correctly
        otion = 2 -> program exits incorrectly (unable to open url)
        '''

        end = datetime.today()
        if option == 1:
            s = '{}, {} NEW ITEMS ADDED. PROCESSING TIME = {}'.format(end, self.collection.count() - self.initial, end - self.start_time)
            print s
            logging.info(s)
        if option == 2:
            s = '{}, URL opening issues, terminating program... {} new items fonund, processing time = {}'.format(end, self.collection.count() - self.initial, end - self.start_time)
            print s
            logging.info(s)




if __name__ == "__main__":
    zxxk = zxxk()
    #zxxk.collect()

    client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
    collection = client.spider.zxxk
    collection_res = client.spider.res
    for d in collection.find({'res_intro': ''}):
        res_intro = ''
        _id = d['_id']
        url = d['res_url']
        try:
            find = pq(unicode(urllib2.urlopen(url).read(), 'utf-8'))
            res_intro = find('div.intro-text').text()
            if res_intro == '':
                print 'nothing found m8'
        except Exception:
            traceback.print_exc()
        print '------------'
        print res_intro
        print '------------'
        collection.update({'_id': _id}, {"$set": {'res_intro': res_intro}}, upsert=False)
        collection_res.update({'res_url': url}, {'$set': {'res_intro': res_intro}}, upsert=False)
