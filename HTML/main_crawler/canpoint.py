# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo,logging, re, sys, time, traceback, urllib2
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class canpoint:

    '''
    Canpoint scraper - Selenium Webdriver
    Last updated: Tuesday, august 7th 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/canpoint.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.spider.canpoint
        self.collection_res = client.spider.res
        self.res_urls = set(self.collection.distinct('res_url'))
        self.document_list = []
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]
        urllib2.install_opener(opener)


    def gk_collect(self):

        '''
        collects from http://gk.canpoint.cn/Search.aspx
        METHOD - traversal through tabs
        '''

        print 'at gk.canpoint'
        driver = webdriver.PhantomJS()
        driver.get('http://gk.canpoint.cn/Search.aspx')
        start_time = datetime.today()
        scount = self.collection.count()
        res_area, res_grade, res_intro, res_class, res_version = '', '高中', '', '', ''

        for i in range(1,10):
            subject_tabs = driver.find_element_by_id('k'+str(i))
            res_subject = subject_tabs.text
            subject_tabs.click()
            for j in range(2,12):
                type_tabs = driver.find_element_by_xpath("//li[@id='tongbu']/a["+str(j)+"]")
                type_tabs.click()
                res_type = type_tabs.text
                EXIT = False

                MAX_PAGE = int(driver.find_element_by_xpath("//span[@class='page']/span[2]").text)
                if MAX_PAGE > 3:
                    MAX_PAGE = 3
                else:
                    MAX_PAGE -= 1

                while MAX_PAGE > 0:
                    for k in range(1,21):
                        try:
                            Title = driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr[@name='sTabletr']["+str(k)+"]//a")
                            res_title = Title.text
                            res_url = Title.get_attribute("href")
                            res_point = int(driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr[@name='sTabletr']["+str(k)+"]/td[3]").text)
                            res_date = dateformat.format_date(driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr[@name='sTabletr']["+str(k)+"]/td[4]").text)
                            res_downcount = int(driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr[@name='sTabletr']["+str(k)+"]/td[5]").text)
                            res_id = res_url[33:-5]
                            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
                            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
                            res_intro = self.get_intro(res_url, gk=True)

                            document = {'res_title': res_title, 'res_url': res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_area': res_area,
                                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id, 'res_file': '', 'site_id': 'canpoint'}

                            print res_url, res_date
                            if self.check_date(res_date, datetime.today()):
                                print 'document too old'
                                EXIT = True
                                break
                            if res_url in self.res_urls:
                                EXIT = True
                                print 'document already exists'
                                break
                            self.res_urls.add(res_url)
                            self.document_list.append(document)
                        except Exception:
                            traceback.print_exc()
                    if EXIT:
                        break
                    MAX_PAGE -= 1
                    driver.find_element_by_xpath("//div[@class='kuang_b']/span[@class='page']/a[3]").click()
                    self.wait_for_load(driver)

        if len(self.document_list) > 0:
            self.collection.insert_many(self.document_list)
            self.collection_res.insert_many(self.document_list)

        end_time = datetime.today()
        s = '{}, FOUND {} NEW ITEMS. PROCESSING TIME: {}'.format(end_time, self.collection.count()-scount, end_time - start_time)
        print s
        logging.info(s)
        self.document_list = []
        driver.quit()


    def zk_collect(self):

        '''
        collects from http://zk.canpoint.cn/
        METHOD - traversal through clicking tabs
        '''

        print 'at zk.canpoint'
        driver = webdriver.PhantomJS()
        driver.get('http://zk.canpoint.cn/')
        start_time = datetime.today()
        scount = self.collection.count()
        res_area, res_grade, res_intro, res_class, res_version = '', '初中', '', '', ''

        for i in range(2,11):
            subject_tabs = driver.find_element_by_xpath("//li[@id='xueke']/a["+str(i)+"]")
            res_subject = subject_tabs.text
            ActionChains(driver).move_to_element(subject_tabs).click(subject_tabs).perform()
            self.wait_for_load(driver)
            for j in range(2,8):
                type_tabs = driver.find_element_by_xpath("//div[@class='bg']/div[@class='menu_right']/ul[@class='nav_a']/li[@id='tongbu']/a["+str(j)+"]")
                ActionChains(driver).move_to_element(type_tabs).click().perform()
                self.wait_for_load(driver)
                res_type = type_tabs.text
                MAX_PAGE = int(driver.find_element_by_xpath("//div[@class='kuang_b']/span[@class='page']/span[2]").text)
                EXIT = False

                if MAX_PAGE > 3:
                    MAX_PAGE = 3
                else:
                    MAX_PAGE -= 1

                while MAX_PAGE > 0:
                    for k in range(1,61, 3):
                        try:
                            Title = driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr["+str(k)+"]/td[1]/a")
                            res_title = re.sub(r"<.*>", "", Title.get_attribute('innerHTML')).strip()
                            res_url = Title.get_attribute("href")
                            res_point = int(driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr["+str(k)+"]/td[3]").text)
                            res_date = dateformat.format_date(driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr["+str(k)+"]/td[4]").text)
                            res_downcount = int(driver.find_element_by_xpath("//table[@id='searchTable']/tbody/tr["+str(k)+"]/td[5]").text)
                            res_id = res_url[33:-5]
                            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
                            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
                            res_intro = self.get_intro(res_url, gk=False)

                            document = {'res_title': res_title, 'res_url': res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_area': res_area,
                                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id, 'res_file': '', 'site_id': 'canpoint'}

                            print res_url, res_date
                            if self.check_date(res_date, datetime.today()):
                                print 'document too old'
                                EXIT = True
                                break
                            if res_url in self.res_urls:
                                EXIT = True
                                print 'document already exists'
                                break
                            self.res_urls.add(res_url)
                            self.document_list.append(document)
                        except Exception:
                            traceback.print_exc()
                    if EXIT:
                        break

                    MAX_PAGE -= 1
                    nextpage = driver.find_element_by_xpath("//div[@class='kuang_b']/span[@class='page']/a[3]")
                    ActionChains(driver).move_to_element(nextpage).click().perform()
                time.sleep(1)

        if len(self.document_list) > 0:
            self.collection.insert_many(self.document_list)
            self.collection_res.insert_many(self.document_list)

        end_time = datetime.today()
        s = '{}, FOUND {} NEW ITEMS. PROCESSING TIME: {}'.format(end_time, self.collection.count()-scount, end_time - start_time)
        print s
        logging.info(s)
        self.document_list = []
        driver.quit()


    def wait_for_load(self, driver):

        '''
        Waits for selenium webdriver to load all html elments on a webpage before
        proceeding to scrape it
        '''

        while True:
            first = driver.find_element_by_xpath('/html').get_attribute('innerHTML')
            time.sleep(0.5)
            second = driver.find_element_by_xpath('/html').get_attribute('innerHTML')
            if first == second:
                break


    def check_date(self, res_date, res_today):

        '''
        If document is older than current Month, deem it as too old to scrape.
        '''

        res_today = res_today.strftime('%Y-%m-%d')
        res_date = res_date.split('-')
        res_today = res_today.split('-')
        return  ((int(res_date[0])==int(res_today[0])) and (int(res_date[1]) < int(res_today[1]))) or (int(res_date[0])<int(res_today[0]))


    def get_intro(self, res_url, gk=True):

        '''
        Opens res_url and gets res_intro. Set gk to False if on zk.canpoint
        '''
        try:
            html =  unicode(urllib2.urlopen(res_url).read(), 'utf-8')
            find = pq(html)
            if gk:
                return find('div.des_down').html().split('<br />')[0].strip()
            else:
                return find('div.jobc p').eq(1).text()
        except Exception:
            traceback.print_exc()
            return ''




if __name__ == '__main__':

    canpoint = canpoint()
    canpoint.gk_collect()
    canpoint.zk_collect()
