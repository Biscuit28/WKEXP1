# -*- coding: utf-8 -*-
from datetime import datetime
from pyquery import PyQuery as pq
import pymongo, sys, logging, urllib2, traceback, requests, cookielib, pprint
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf

class ht88_2:

    def __init__(self):

        logfile = '/opt/spider/logs/ht88_2.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.current_url = 0
        self.collection = client.spider.ht88
        self.collection_res = client.spider.res
        self.res_urls = set([])
        self.start_time = datetime.today()
        self.initial = self.collection.count()
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        self.subject_dict = {'www': '语文', 'shuxue': '数学', 'yingyu': '英语',
                            'wuli': '物理', 'huaxue': '化学', 'shengwu': '生物',
                            'lishi': '历史', 'dili': '地理', 'zhengzhi': '政治'}
        self.key_list = self.subject_dict.keys()

        # self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        #                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #                 'Accept-Encoding':  'gzip, deflate',
        #                 # 'Accept-Language':	'en-US,en;q=0.8',
        #                 # 'Upgrade-Insecure-Requests':	'1',
        #                 # 'Cache-Control':	'max-age=0',
        #                 # 'Host': 'www.ht88.com'
        #                 }
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)

        #TODO find ways to increase speeed

    def read_url(self, url_key, res_id, tries=10, get_intro=False):

        '''
        Reads html from url. Each url is given 10 tries before it is scrapped
        '''
        if not get_intro:
            target = 'http://'+url_key+'.ht88.com/downinfo/'+str(res_id)+'.html'
        else:
            target = 'http://'+url_key+'.ht88.com/user/ViewdownHits.asp?ID='+str(res_id)
        while tries > 0:
            try:
                #self.headers['Host'] = url_key+'.ht88.com'
                # w = requests.get(target, headers=self.headers)
                # print w.headers
                # html = unicode(w.content, 'gb18030')
                html = unicode(urllib2.urlopen(target).read(), 'gb18030')
                if u'该页面不存在，可能的原因' in html:
                    return False
                else:
                    return html
            except urllib2.HTTPError, e:
                if e.code == 404:
                    return False
                else:
                    tries -= 1
            except Exception, e:
                #traceback.print_exc()
                print e
                #print target
                tries -= 1
        self.logging(2)
        quit()


    def get_info(self, url_key, res_id, html):

        '''
        Reads all relevant data from selected download page
        '''
        try:
            d = pq(html)
            res_url = 'http://'+url_key+'.ht88.com/downinfo/'+str(res_id)+'.html'
            res_subject = self.subject_dict[url_key]
            res_title = d('#book h1').text()
            res_date = dateformat.format_date(d('#info li').eq(5).remove('strong').text())
            res_data = d('#info li').eq(1).remove('strong').text().split('/')
            res_version = res_data[0]
            res_type = res_data[2].strip()
            res_grade = res_data[1].strip()[0:2]
            res_intro = d('#description dd').text()
            num_data = self.read_url(url_key, res_id, get_intro=True).split(';')
            res_downcount = int(filter(unicode.isdigit, num_data[4]))
            res_point = int(filter(unicode.isdigit, num_data[6]))
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, '')
            crawl_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_grade': res_grade,
                        'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version, 'res_province': res_province,
                        'res_city': res_city, 'res_county': res_county, 'res_id': res_id,'res_file': '',
                        'site_id': 'ht88', 'date': crawl_date}

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


    def try_keys(self, curr_key, res_id):

        '''
        upon finding that an increment with the current key does not work,
        method will cycle through all the keys (starting from current key) until
        it finds a key that works. if it cannot find one, it will return false.
        which it will take  as a sign for bad count. ie it will skip it
        '''
        url_keys = self.key_list
        url_keys.insert(0, url_keys.pop(url_keys.index(curr_key)))
        for url_key in url_keys:
            result = self.read_url(url_key, res_id)
            if not result:
                continue
            else:
                return (result, url_key)
        return False


    def collect(self, range=False):

        '''
        Collects from 'http://SUBJECT_KEY.ht88.com/downinfo/LATEST_RES_ID.html
        METHOD - Traversal through incrementing res_id

        NEW - optional range arugment is a list [a,b] where documents are retrieved
        from the a to b non-inclusive, ie if  a=2, b=5, the range is (2,3,4)
        '''
        url_key = 'www'
        if not range:
            if self.initial == 0: #745688
                data = self.try_keys(url_key, 745688)
                self.get_info(data[1], 745688, data[0]) #2017-01-01
            doc = self.collection.find({}).sort('res_id', -1).limit(1)[0]
            r_id = doc['res_id']
            max_id = float('inf')
        else:
            self.res_urls = set(self.collection.distinct('res_url'))
            r_id = range[0] - 1
            max_id = range[1]

        print 'starting at ', r_id + 1

        while True:
            BAD_COUNT = 0
            while BAD_COUNT <= 50:
                r_id += 1
                self.current_url = r_id
                data = self.try_keys(url_key, r_id)
                if not data:
                    BAD_COUNT += 1
                    print 'bad url', BAD_COUNT
                else:
                    url_key = data[1]
                    break
            if BAD_COUNT > 50 or r_id >= max_id+1:
                self.logging(1)
                quit()
            self.get_info(url_key, r_id, data[0])
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
    ht88 = ht88_2()
    ht88.collect([745836, float('inf')])
