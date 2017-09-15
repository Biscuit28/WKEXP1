# -*- coding: utf-8 -*-
from datetime import datetime
import traceback, pymongo, sys, os, logging, requests
from selenium import webdriver
from dltools import tools

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf


class dearedu_dl:

    '''
    Dearedu Downloader. Previous implementation seems to be not working anymore
    :c

    Uses Selenium Webdriver (Chrome driver) + Requests

    Last Updated: Friday, August 11th 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/deareduDownload.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.spider.dearedu
        self.collection_res = client.spider.res
        self.sim_collection = client.spider.similar
        self.count = 0


    def download(self):

        '''
        Uses Selenium Webdriver Chrome (Headless). This is because logging in with
        urllib2, request etc.. seems to be not working? Apparentely if platform is
        windows this program will not run

        NOTE need chrome >= 59 to run this
        '''

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=options)

        try:
            driver.get('http://club.dearedu.com/member/index.php')
            driver.find_element_by_name('userid').send_keys('robota')
            driver.find_element_by_name('pwd').send_keys('!QAZxsw2')
            driver.find_element_by_xpath("//input[@class='loginbutton']").click()
        except Exception, e:
            traceback.print_exc()
            driver.close()

        ms = requests.session()
        ms.headers.update({'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})

        for doc in self.collection.find({'$and': [{'res_file': ''}, {'res_point': '免费'}]}):
            res_url = doc['res_url']
            try:
                _id, res_id = doc['_id'], doc['res_id']
                res_date = doc['res_date'].replace('-', ' ').split()
                driver.get(res_url)
                dlurl = driver.find_element_by_xpath("//div[@class='xz_xunlei']/div[@class='xz_x1']/a[1]").get_attribute("href")
                result = ms.get(dlurl)
                scode = result.status_code
                if scode == 200:
                    ext = result.headers['Content-Disposition']
                    extension = tools.get_extension(ext)
                    filename = '{}.{}'.format(res_id, extension)
                    filepath = '/opt/file/dearedu/{}/{}/{}'.format(res_date[0], res_date[1],filename)

                    if not os.path.exists(os.path.dirname(filepath)):
                        try:
                            os.makedirs(os.path.dirname(filepath))
                        except OSError as exc:
                            if exc.errno != errno.EEXIST:
                                raise
                    with open(filepath, 'wb') as f:
                        f.write(result.content)

                    self.sim_collection.update({'o_url': res_url}, {"$set": {'o_file': filepath}}, upsert=False, multi=True)
                    self.collection.update({'_id': _id}, {"$set": {'res_file': filepath}}, upsert=False
                    self.collection_res.update({'res_url': res_url}, {"$set": {'res_file': filepath}}, upsert=False)
                    self.count += 1
                    print 'downloaded {} ---> {}, {}'.format(filename, filepath, self.count)
                else:
                    s = 'Error downloading {}, code = {}'.format(res_url, scode)
                    print s
                    logging.info(s)
            except Exception, e:
                traceback.print_exc()
                logging.info('{}, Download {} failed, Reason {}'.format(datetime.today(), res_url, e))
                continue
            except KeyboardInterrupt:
                driver.quit()
                sys.exit()
        s = '{}, {} new items downloaded'.format(datetime.today(), self.count)
        print s
        logging.info(s)



if __name__ == "__main__":
    dearedu = dearedu_dl()
    dearedu.download()
