# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo,logging, time, sys, os, urllib, urllib2, traceback
from pyquery import PyQuery as pq
from dltools import tools

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf


class HT88_dl:

    '''
    uses urllib2 and urllib to download documents from ht88.com
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/ht88Download.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        self.p_link = 'http://m.ht88.com/user/ajax_vipdownload.asp?act=1&ID='
        self.count = 0
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.spider.ht88
        self.sim_collection = client.spider.similar
        self.collection_res = client.spider.res


    def download(self):

        START_TIME = datetime.today()
        for doc in self.collection.find({'res_point': 0}):
            try:
                _id, res_id = doc['_id'], doc['res_id']
                res_date = doc['res_date'].replace('-', ' ').split()
                text = urllib2.urlopen(self.p_link + str(res_id), timeout=60).read()
                html = urllib.unquote(text)
                d = pq(html)
                download_url = d('li a').eq(0).attr('href')
                extension = tools.get_extension(download_url)
                filename = '{}.{}'.format(res_id, extension)
                filepath = '/opt/file/ht88/{}/{}/{}'.format(res_date[0], res_date[1],filename)

                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise
                urllib.urlretrieve(download_url, filepath)

                self.sim_collection.update({'o_url': doc['res_url']}, {"$set": {'o_file': filepath}}, upsert=False, multi=True)
                self.collection.update({'_id': doc_id}, {"$set": {'res_file': filepath}}, upsert=False)
                self.collection_res.update({'res_url': doc['res_url']}, {"$set": {'res_file': filepath}}, upsert=False)
                self.count += 1
                print 'downloaded {} --> {}   {}'.format(filepath, download_url, self.count)
            except Exception, e:
                traceback.print_exc()
                s = '{}, Download failed, Reason {}'.format(datetime.today(), e)
                logging.info(s)
        s = '{}, {} new items downloaded. Time taken: {}'.format(datetime.today(), self.count, datetime.today() - START_TIME)
        print s
        logging.info(s)



if __name__ == '__main__':

    ht88 = HT88_dl()
    ht88.download()
