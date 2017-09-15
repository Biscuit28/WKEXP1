# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo, logging, time, sys, traceback
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from tools import dateformat, get_grade, get_area

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf
#appr


class xiangpi:

    '''
    Xiangpi scraper - Selenium Webdriver
    Last Updated: Thursday, August 10th 2017
    '''

    def __init__(self):

        logfile = '/opt/spider/logs/xiangpi.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.spider.xiangpi
        self.collection_res = client.spider.res
        self.document_list = []
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()


    def collect(self):

        '''
        collects from http://www.xiangpi.com/zujuan/3/1-0-0-0-0/
        METHOD - traversal through tabs
        '''

        scount = self.collection.count()
        start_time = datetime.today()
        res_type, res_version, res_intro, res_point = '', '', '', ''
        driver = webdriver.PhantomJS()
        driver.get('http://www.xiangpi.com/zujuan/3/1-0-0-0-0/')
        for i in range(1, 4):
            grade_tabs = driver.find_element_by_xpath("//div[@id='tabEduLevels']/a[" + str(i) + "]")
            res_grade = grade_tabs.text
            ActionChains(driver).move_to_element(grade_tabs).click().perform()
            time.sleep(1)
            if i == 1: #Highschool
                subjects = 9
            if i == 2: #junior high
                subjects = 8
            if i == 3: #Elementary
                subjects = 2
            for j in range(1,subjects+1):
                subject_tabs = driver.find_element_by_xpath("//div[@id='tabChapterSubjects']/a[" + str(j) + "]")
                res_subject = subject_tabs.text
                ActionChains(driver).move_to_element(subject_tabs).click().perform()
                EXIT = False
                time.sleep(1)

                MAX_PAGE = 0
                article_count = int(driver.find_element_by_id('paperTotal').text)
                if article_count !=0:
                    MAX_PAGE = article_count/15 + 1
                    if MAX_PAGE > 2:
                        MAX_PAGE = 2

                for l in range(2, MAX_PAGE + 2):
                    pages = driver.find_element_by_xpath("//div[@id='paperListPage']/a[" + str(l) + "]")
                    ActionChains(driver).move_to_element(pages).click().perform()
                    time.sleep(1)
                    for m in range(1, 16):
                        try:
                            Title = driver.find_element_by_xpath("//ul[@id='paperListCotent']/li[" + str(m) + "]/p[2]/a")
                            res_title = Title.text
                            res_class = driver.find_element_by_xpath("//ul[@id='paperListCotent']/li[" + str(m) + "]/p[3]/a[1]").text
                            res_downcount = int(driver.find_element_by_xpath("//ul[@id='paperListCotent']/li[" + str(m) + "]/p[5]").text)
                            res_date = dateformat.format_date(driver.find_element_by_xpath("//ul[@id='paperListCotent']/li[" + str(m) + "]/p[6]").text)
                            res_area = driver.find_element_by_xpath("//ul[@id='paperListCotent']/li[" + str(m) + "]/p[3]/a[3]").text
                            res_url = Title.get_attribute("href")
                            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
                            (res_grade, res_class) = self.gc_extractor.extraction(res_title, res_grade, res_class)
                            res_id = int(filter(str.isdigit, str(res_url)))

                            document = {'res_title': res_title, 'res_url':res_url, 'res_date': res_date, 'res_downcount': res_downcount,
                                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_area': res_area,
                                        'res_grade': res_grade, 'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id': res_id, 'res_file': '', 'site_id': 'xiangpi'}

                            print res_url, res_date
                            if self.check_date(res_date, datetime.today()):
                                print 'document too old'
                                EXIT = True
                                break
                            if self.collection.find_one({'res_url': res_url}):
                                EXIT = True
                                print 'document already exists'
                                break
                            self.document_list.append(document)
                        except Exception:
                            traceback.print_exc()
                    if EXIT:
                        break

        if len(self.document_list) > 0:
            self.collection.insert_many(self.document_list)
            self.collection_res.insert_many(self.document_list)

        end_time = datetime.today()
        s = '{}, FOUND {} NEW ITEMS. PROCESSING TIME: {}'.format(end_time, self.collection.count()-scount, end_time - start_time)
        print s
        logging.info(s)
        driver.quit()


    def check_date(self, res_date, res_today):

        '''
        If document is older than current Month, deem it as too old to scrape.
        '''

        res_today = res_today.strftime('%Y-%m-%d')
        res_date = res_date.split('-')
        res_today = res_today.split('-')
        return  ((int(res_date[0])==int(res_today[0])) and (int(res_date[1]) < int(res_today[1]))) or (int(res_date[0])<int(res_today[0]))




if __name__ == '__main__':

    xiangpi = xiangpi()
    xiangpi.collect()
