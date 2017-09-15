# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, traceback
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class dearedu_2:

    '''
    Dearedu_2 scraper - Urllib2 (New crawl method for dearedu)
    Last Updated: Tuesday, August 23rd 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/dearedu_2.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.current_url = 0
        self.collection = client.spider.dearedu
        self.collection_res = client.spider.res
        self.res_urls = set([])
        self.start_time = datetime.today()
        self.initial = self.collection.count()
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)


    def read_url(self, target, tries=10):

        '''
        Reads html from url and encodes it utf-8. Each url is given 10 tries
        before it is scrapped
        '''
        while tries > 0:
            try:
                urlobj = urllib2.urlopen(target, timeout=5)
                return(unicode(urlobj.read(), 'utf-8'))
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
            res_downcount = ''
            class_subject = d('.xq_goo ul li').eq(3).find('span a').text().split()
            res_class = class_subject[0]
            res_subject = class_subject[1]
            res_title = d('.xq_h.xq_sdhahdwq ul li a').text()
            res_date = dateformat.format_date(d('.xq_goo ul li').eq(0).text().split()[1])
            res_point = d('.xq_goo ul li').eq(4).find('span font').text()
            res_type = d('.xq_goo ul li').eq(2).find('span a').eq(0).text()
            res_version = d('.xq_goo ul li').eq(1).find('span a').eq(0).text()
            res_intro = d('#contenthuidai').text()
            crawl_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            try:
                res_point = int(filter(unicode.isdigit, res_point))
            except:
                pass
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            (res_grade, res_class) = self.gc_extractor.extraction(res_title, '', res_class)

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type,
                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id,
                        'res_file': '', 'site_id': 'dearedu', 'date': crawl_date}

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
        Collects from http://s.dearedu.com/downs/p-LAST_RES_ID.html
        METHOD - Traversal through incrementing res_id

        NEW - optional range arugment is a list [a,b] where documents are retrieved
        from the a to b non-inclusive
        '''

        main_url = 'http://s.dearedu.com/downs/p-'
        if not range:
            if self.initial == 0:
                self.get_info(self.read_url('http://s.dearedu.com/downs/p-4152000.html'), 'http://s.dearedu.com/downs/p-4152000.html', 4152000)
            doc = self.collection.find({}).sort('res_id', -1).limit(1)[0]
            r_id = int(filter(unicode.isdigit, doc['res_url']))
            max_id = float('inf')
        else:
            self.res_urls = set(self.collection.distinct('res_url'))
            r_id = range[0]
            max_id = range[1]

        print 'starting at ', r_id + 1

        while True:
            BAD_COUNT = 0
            while BAD_COUNT <= 50:
                r_id += 1
                self.current_url = r_id
                url = 'http://s.dearedu.com/downs/p-'+str(r_id)+'.html'
                html = self.read_url(url)
                if len(html) < 100: #implies that our html is a bit short, probably an error
                    BAD_COUNT += 1
                    print BAD_COUNT, 'bad url'
                else:
                    break
            if BAD_COUNT > 50 or r_id >= max_id+1:
                break
            self.get_info(html, url, r_id)
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
            s = '{}, URL opening issues at {}, terminating program... {} new items fonund, processing time = {}'.format(end, self.current_url,  self.collection.count() - self.initial, end - self.start_time)
        logging.info(s)
        print s


if __name__ == '__main__':
    dearedu = dearedu_2()
    dearedu.collect()
    #dearedu.collect([4153143, 4353400])
