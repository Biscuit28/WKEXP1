# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo,logging, time, sys, os, cookielib, requests, traceback
from dltools import tools

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr

class canpoint_dl:

    '''
    uses requests.session to download documents from canpoint
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/canpointDownload.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)

        self.collection = client.spider.canpoint
        self.collection_res = client.spider.res
        self.sim_collection = client.spider.similar
        self.user_collection = client.robots.canpoint
        self.tired_bots = []
        self.mySession = None
        self.cj = None
        self.count = 0
        self.robot_points = None
        self.username = None
        self.exit = False


    def log_in(self, point):

        self.username == None
        for robot in self.user_collection.find({'r_hp': {'$gte': point}}):
            if robot['r_name'] not in self.tired_bots:
                self.username = robot['r_name']
                self.robot_points = robot['r_hp']
                print 'robot -- {} -- going to work!'.format(self.username)
                break
        if self.username == None:
            s = '{}, all robots are exhausted :C , quitting...'.format(datetime.today())
            print s
            logging.info(s)
            self.exit = True
            return
        self.cj = cookielib.CookieJar()
        self.mySession = requests.session()
        self.mySession.headers.update({'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})
        res = self.mySession.get('http://gk.canpoint.cn/login/loginuser.ashx?ln='+self.username+'&lp=111111&cp=0', cookies = self.cj)


    def download_documents(self, paid=False):

        start = datetime.today()

        self.exit = False

        if paid:
            print 'downloading paid documents'
            condition = {'res_point': {'$gte': 1}}
        if not paid:
            print 'downloading free documents'
            condition = {'res_point': 0}
        for doc in self.collection.find({'$and': [{'res_file': ''}, condition]}).sort('res_point', 1):
            self.download(doc)
            if self.exit:
                return
        s = '{}, {} new items downloaded. Time taken: {}'.format(datetime.today(), self.count, datetime.today() - start)
        print s
        logging.info(s)


    def download(self, doc):

        try:
            date = doc['res_date'].replace('-', ' ').split()
            res_url, doc_id, res_point = doc['res_url'], doc['_id'], doc['res_point']
            docid = doc['res_id']
            print '{} ----> respoint {}'.format(doc['res_url'], res_point)
            if self.robot_points == None and not self.exit:
                self.log_in(res_point)
            if (res_point > self.robot_points) and not self.exit:
                print '{} does not have enough hp to continue,  {} rp > {} hp'.format(self.username, res_point, self.robot_points)
                self.log_in(res_point)
            if self.exit:
                return
            response = self.mySession.post(res_url[0:22] + 'DownFile.aspx', data={'docid': docid}, cookies=self.cj)
            if 'Content-Disposition' not in response.headers:

                if u'您不是VIP用户,不允许下载4星和顶级资料' in response.text:
                    print '{} is a VIP only document. Robot cannot access.'.format(doc['res_url'])
                    return
                elif u'每天下载上限为50' in response.text:
                    print 'robot {} is exhausted. trying with a new one'.format(self.username)
                    self.tired_bots.append(self.username)
                    self.cj.clear()
                    self.mySession.close()
                    self.log_in(res_point)
                    self.download(doc)
                    return
                elif u'你的剩余积分不足' in response.text:
                    print 'robot points is too low. robot hp is probably corrupt. RESET HP TO 0'
                    self.user_collection.update({'r_name': self.username}, {"$set": {'r_hp': 0}}, upsert=False)
                    self.cj.clear()
                    self.mySession.close()
                    self.log_in(res_point)
                    self.download(doc)
                    return
                else:
                    print 'unknown error, terminating process'
                    print response.text
                    quit()

            extension = tools.get_extension(response.headers['Content-Disposition'])
            filename = '{}.{}'.format(docid, extension)
            filepath = '/opt/file/canpoint/{}/{}/{}'.format(date[0], date[1], filename)

            if not os.path.exists(os.path.dirname(filepath)):
                try:
                    os.makedirs(os.path.dirname(filepath))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            with open(filepath, 'wb') as f:
                f.write(response.content)

            self.robot_points -= res_point
            self.user_collection.update({'r_name': self.username}, {"$set": {'r_hp': self.robot_points}}, upsert=False)
            self.sim_collection.update({'o_url': doc['res_url']}, {"$set": {'o_file': filepath}}, upsert=False, multi=True)
            self.collection.update({'_id': doc_id}, {"$set": {'res_file': filepath}}, upsert=False)
            self.collection_res.update({'res_url': doc['res_url']}, {"$set": {'res_file': filepath}}, upsert=False)
            self.count += 1
            print 'downloaded {} ---> {}, {}'.format(filename, filepath, self.count)
        except Exception, e:
            traceback.print_exc()
            s = '{},Download failed, reason: {}'.format(datetime.today(), e)
            logging.info(s)


if __name__ == '__main__':

    test = canpoint_dl()
    test.download_documents(paid=True)
    test.download_documents(paid=False)
