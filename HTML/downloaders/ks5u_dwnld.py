# -*- coding: UTF-8 -*-
from datetime import datetime
import pymongo,logging, urllib2, urllib, cookielib, os, errno, sys, traceback
from dltools import tools

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr

class ks5u_dwnld:

    '''
    uses urllib2 and urllib to download documents from ks5u.com
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/ks5uDownload.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        self.username = "834023473@qq.com" #26091278@qq.com
        self.password = "1234qwer"
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.spider.ks5u
        self.sim_collection = client.spider.similar
        self.collection_res = client.spider.res


    def log_in(self):

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)
        target = 'http://www.ks5u.com/user/inc/UserLogin_Index.asp'
        payload = {'username': self.username, 'password': self.password, 'c_add': 0}
        data = urllib.urlencode(payload)
        req = urllib2.Request(target, data)
        response = urllib2.urlopen(req)


    def download_documents(self):

        START_TIME = datetime.today()
        self.log_in()
        COUNT = 0
        cdcount = 0

        for doc in self.collection.find({'$and': [{'res_file': ''}, {'res_point': 0}]}):
            try:
                res_id = str(doc['res_id'])
                doc_id = doc['_id']
                res_date = doc['res_date'].replace('-', ' ').split()
                link = 'http://www.ks5u.com/USER/INC/DownCom.asp?id='+ res_id
                req = urllib2.Request(link)
                download_url = urllib2.urlopen(req).geturl()
                req = urllib2.Request(download_url, headers={"Referer": doc['res_url']})
                response = urllib2.urlopen(req)
                headers = response.headers
                content_disposition = headers.getheader('content-disposition')
                if content_disposition == None:
                    cdcount += 1
                    print "cannot download", download_url, '(content_disposition not found)', cdcount
                    print "doc info: ", doc['res_url']
                    if cdcount > 30:
                        break
                    continue
                cdcount = 0
                extension = tools.get_extension(content_disposition)
                filename = '{}.{}'.format(res_id, extension)
                filepath = '/opt/file/ks5u/{}/{}/{}/{}'.format(res_date[0], res_date[1], res_date[2], filename)

                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise
                with open(filepath, 'wb') as f:
                    f.write(response.read())

                print 'downloaded {} --> {}'.format(filepath, download_url)
                doc['res_file'] = filepath
                self.sim_collection.update({'o_url': doc['res_url']}, {"$set": {'o_file': filepath}}, upsert=False, multi=True)
                self.collection.update({'_id': doc_id}, {"$set": doc}, upsert=False)
                self.collection_res.update({'res_url': doc['res_url']}, {"$set": {'res_file': filepath}}, upsert=False)
                COUNT += 1
            except Exception, e:
                traceback.print_exc()
                s = '{}, Download failed, Reason {}'.format(datetime.today(), e)
                logging.info(s)
        s = '{}, {} new items downloaded. Time taken: {}'.format(datetime.today(), COUNT, datetime.today() - START_TIME)
        print s
        logging.info(s)



if __name__ == '__main__':
    ks5u = ks5u_dwnld()
    ks5u.download_documents()

    #http://www.ks5u.com/USER/INC/DownCom.asp?id=2773841            #link 1
    #http://www.ks5u.com/USER/INC/ToDownUrlPt.asp?id=2774111        #link 2
