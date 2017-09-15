# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo,logging, time, sys, os, requests, traceback
from pyquery import PyQuery as pq
from dltools import tools

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr

#DEPRECATED


class Dearedu_dl:

    '''
    uses requests.sessions to download documents from dearedu.com
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/deareduDownload.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.spider.dearedu
        self.sim_collection = client.spider.similar

        self.main = 'http://club.dearedu.com/plus/down4.php?url='
        self.count = 0


    def download(self):

        START_TIME = datetime.today()

        mySession = requests.session()
        mySession.headers.update({'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})

        for doc in self.collection.find({'$and': [{'res_file': ''}, {'res_point': '免费'}]}):

            res_url = doc['res_url']

            try:
                _id, res_id = doc['_id'], doc['res_id']
                res_date = doc['res_date'].replace('-', ' ').split()

                html = mySession.get(res_url).text
                html_search = pq(html)

                partial_url = html_search('div.hidden_x.sadasqw_sa_s iframe').eq(0).attr('src').replace('http://officeweb365.com/o/?i=5635&furl=', '')
                download_url = self.main + partial_url + '&title=' + str(res_id)

                extension = tools.get_extension(partial_url)

                filename = '{}.{}'.format(res_id, extension)
                filepath = '/opt/file/dearedu/{}/{}/{}'.format(res_date[0], res_date[1],filename)

                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise

                file = mySession.get(download_url)

                with open(filepath, 'wb') as f:
                    f.write(file.content)

                self.sim_collection.update({'o_url': res_url}, {"$set": {'o_file': filepath}}, upsert=False, multi=True)
                self.collection.update({'_id': _id}, {"$set": {'res_file': filepath}}, upsert=False)

                self.count += 1

                print 'downloaded {} ---> {}, {}'.format(filename, filepath, self.count)

            except Exception, e:
                print res_url
                traceback.print_exc()
                s = '{}, Download failed, Reason {}'.format(datetime.today(), e)
                logging.info(s)

        s = '{}, {} new items downloaded. Time taken: {}'.format(datetime.today(), self.count, datetime.today() - START_TIME)
        print s
        logging.info(s)



if __name__ == '__main__':

    test = Dearedu_dl()
    test.download()
