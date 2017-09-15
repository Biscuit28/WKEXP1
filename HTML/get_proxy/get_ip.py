# -*- coding: utf-8 -*-
from datetime import *
from selenium import *
from selenium import webdriver
from PIL import Image, ImageEnhance, ImageFilter
from pyquery import PyQuery as pq
import pymongo,logging, time, re, urllib2, signal, pytesseract


class get_ip:

    #GETS IP AND STUFF

    def __init__(self):

        client = pymongo.MongoClient('10.1.1.13', 27017)
        self.collection = client.config.proxy
        self.objectives = {'gkcanpoint': 'http://gk.canpoint.cn/Search.aspx', 'zkcanpoint':'http://zk.canpoint.cn/',
        'dearedu':'http://s.dearedu.com/list.php?g=1&', 'ht88':'http://www.ht88.com', 'tl100':'http://taoti.tl100.com',
         'xiangpi':'http://www.xiangpi.com/zujuan/3/1-0-0-0-0/', 'daliankao': 'http://www.daliankao.org', 'ks5u': 'http://www.ks5u.com',
         'hengqian': 'http://eng.hengqian.com', 'jb1000':'http://www.jb1000.com/Service/Map.html', 'jtyhjyGaozhong':'http://www.jtyhjy.com/zyw/synclass/home',
         'twentyOneCnjy': "https://www.21cnjy.com/kejian/", 'xueyou':'http://www.gkstk.com/guide/beike/', 'ziyuanku': "http://www.ziyuanku.com/leixing/"}

        self.valid_ips = []


    def url_user_agent(self, proxy,url, t):

        proxy_support = urllib2.ProxyHandler({'http':proxy})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        i_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
        req = urllib2.Request(url,headers=i_headers)
        html = urllib2.urlopen(req,timeout=t)
        if url == html.geturl():
            doc = html.read()
            return doc
        return


    def verify_ips_quick(self, ips):
        '''
        Verifies IP to see if proxy works. modified from something guoxing found online
        '''
        LENGTH, COUNT, FOUND = len(ips), 1, 0
        for ele in ips:
            IP, PORT = ele[0], ele[1]
            IPPORT = IP+':'+PORT

            try:
                url = 'http://httpbin.org/get?show_env=1'
                doc = self.url_user_agent(IPPORT ,url, 2)
                self.valid_ips.append(IPPORT)
                FOUND += 1
                print 'success'
            except Exception, e:
                print e

            print str(COUNT) + "/" + str(LENGTH)
            COUNT += 1

        print str(FOUND) +  ' ips waiting for further testing'


    def read_url(self, target):
        '''
        Reads the target url
        '''
        return urllib2.urlopen(target, timeout=30).read()


    def from_kuaidaili(self):
        '''
        Gets ip from kuaidaili of current date
        '''
        print "starting kuaidaili"
        curr_date = datetime.today().strftime('%Y-%m-%d')

        URL = 'http://www.kuaidaili.com/free/inha/'
        driver = webdriver.PhantomJS()
        ips = []

        def get_ip(MAIN_URL):

            driver.get(MAIN_URL)
            for i in range(1, 16):
                IP = driver.find_element_by_xpath("//div[@id='list']/table/tbody/tr[" + str(i) + "]/td[@data-title='IP']").text
                PORT = driver.find_element_by_xpath("//div[@id='list']/table/tbody/tr[" + str(i) + "]/td[@data-title='PORT']").text
                DATE = driver.find_element_by_xpath("//div[@id='list']/table/tbody/tr[" + str(i) + "]/td[@data-title='最后验证时间']").text
                DATE = DATE[:10]
                if DATE != curr_date:
                    print '{} is expired ({}), we need IPS of current date ({})'.format(IP+':'+PORT, DATE, curr_date)
                    return False
                print IP + ':' + PORT + '  --> ' + DATE
                ips.append([IP, PORT])
            return True

        PAGE = 1
        while get_ip(URL + str(PAGE)):
            PAGE += 1

        self.verify_ips_quick(ips)

        driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()
        print 'done'


    def from_proxy360(self):
        '''
        Gets ip from proxy360. proxy 360 is only 1 single page so we get it all
        regardless of date
        '''
        print "starting proxy360"
        MAIN_URL = 'http://www.proxy360.cn/default.aspx'
        driver = webdriver.PhantomJS()
        driver.get(MAIN_URL)
        ips = []

        for content in driver.find_elements_by_xpath("//div[@id='ctl00_ContentPlaceHolder1_upProjectList']/div[@name='list_proxy_ip']"):
            content_text = content.text
            L = content_text.split()
            print L[0] + ':' + L[1]
            ips.append([L[0],L[1]])

        self.verify_ips_quick(ips)

        print 'done'


    def from_66ip(self):
        '''
        Gets IP from 66ip of current date
        '''
        print "starting 66ip"
        URL = 'http://www.66ip.cn/'
        AREA_INDEX = 'areaindex_1/'
        ips = []

        def get_ip(MAIN_URL):

            r = pq(self.read_url(MAIN_URL))
            curr_date = datetime.today().strftime('%Y%m%d')

            for items in r('tr').items():
                text = items.text().split()
                if len(text) > 2:
                    if text[1].isdigit():
                        DATE = filter(lambda x: x.isdigit(), text[4])[:-2]
                        print text[0] + ':' + text[1] + '  --> ' + DATE
                        if DATE != curr_date:
                            print '{} is expired ({}), we need IPS of current date ({})'.format(text[0]+':'+text[1], DATE, curr_date)
                            return False
                        ips.append([text[0], text[1]])
            return True

        PAGE = 1
        while get_ip(URL + str(PAGE) + '.html'):
            PAGE += 1

        PAGE = 1
        while get_ip(URL + AREA_INDEX + str(PAGE) + '.html'):
            PAGE += 1

        self.verify_ips_quick(ips)

        print 'done'


    def from_nianshao(self):
        '''
        Gets ip from nianshao of current date
        '''
        print "starting nianshao"
        ips = []
        HTTP = 'http://www.nianshao.me/?stype=1'
        HTTPS = 'http://www.nianshao.me/?stype=2'
        OTHER = 'http://www.nianshao.me/?stype=5'
        ANDPAGE = '&page='

        def get_ip(MAIN_URL):

            r = pq(self.read_url(MAIN_URL))
            curr_date = datetime.today().strftime('%Y-%m-%d').replace("-0","-")

            for items in r('tr').items():
                text = items.text().split()
                if len(text) > 2:
                    if text[1].isdigit():
                        print text[0] + ':' + text[1] + '  --> ' + text[5]
                        if text[5] != curr_date:
                            print '{} is expired ({}), we need IPS of current date ({})'.format(text[0]+':'+text[1], text[5], curr_date)
                            return False
                        ips.append([text[0], text[1]])

            return True

        PAGE = 1
        while get_ip(HTTP + ANDPAGE + str(PAGE)):
            PAGE += 1

        PAGE = 1
        while get_ip(HTTPS + ANDPAGE + str(PAGE)):
            PAGE += 1

        PAGE = 1
        while get_ip(OTHER + ANDPAGE + str(PAGE)):
            PAGE += 1

        self.verify_ips_quick(ips)

        print 'done'


    def from_mimvp(self):
        '''
        Gets ip from mimvp. We get the entire page because it is only a single page
        NOTE it could be possible that the ocr could have read the image port wrong

        *Need to be careful
        '''
        ips = []
        URL = 'http://proxy.mimvp.com/'
        print "starting mimvp"

        def get_ip(MAIN_URL):

            def read_captcha(img_name):

                image_file = Image.open(img_name) # open colour image
                image_file.save(img_name)
                image_file = image_file.convert('1') # convert image to black and white
                text = pytesseract.image_to_string(Image.open(img_name))
                original_text = text
                text = text.replace('E','8')
                text = text.replace('B', '8')
                text = text.replace('o', '0')
                if text == '8ssa':
                    text = '8998'
                if text == 'sass':
                    text = '9999'
                if text == '3000':
                    text = '9000'
                if text == '8a':
                    text = '88'
                if text == '3737':
                    text = '9797'
                print original_text + '-->' + text
                return text

            def get_image(url, img_name):

                FILE = urllib2.urlopen(url)
                IMAGE = FILE.read()
                open(img_name, 'wb').write(IMAGE)

            r = pq(self.read_url(MAIN_URL))
            curr_date = datetime.today().strftime('%Y-%m-%d')

            for items in r('tr').items():
                text = items.text().split()
                if text[0].isdigit():
                    IP = items('td').eq(1).text()
                    IMG_SRC = URL + items('td img').attr('src')
                    get_image(IMG_SRC, 'mimvp.png')
                    PORT = read_captcha('mimvp.png')
                    DATE = items('td').eq(8).text()
                    DATE = DATE[:10]
                    print IP + ':' + PORT + '  --> ' + DATE
                    if DATE != curr_date:
                        print '{} is expired ({}), we need IPS of current date ({})'.format(IP+':'+PORT, DATE, curr_date)
                        return False
                    ips.append([IP, PORT])
            return True

        get_ip('http://proxy.mimvp.com/index.php?pageindex=cn')
        self.verify_ips_quick(ips)

        print 'done'


    def clear_collection(self):
        '''
        drops the proxy collection entierly. Should be used in conjuction with
        getting new ips
        '''
        print 'removing all proxies'
        now = str(datetime.today())
        self.collection.drop()
        f = open('last_clear.txt', 'w')
        f.write(now)
        f.close()


    def run_friendly(self):
        '''
        runs with user input
        '''
        with open('last_clear.txt') as f:
            for l in f:
                last_cleared = l

        print "Do you wish to clear collection (last_cleared {})?".format(last_cleared)
        print "This will remove all proxies in the database (Y/N)"

        while True:
            del_collection = raw_input("your response: ")
            if del_collection == "Y" or del_collection == "y":
                self.clear_collection()
                break
            if del_collection == "N" or del_collection == "n":
                break

        print "Please select IP source (enter number)"
        print "     from kuaidaili           --> press 1"
        print "     from proxy360            --> press 2"
        print "     from 66ip                --> press 3"
        print "     from nianshao            --> press 4"
        print "     from mimvp (INCOMPLETE)  --> press 5"
        print "     RUN ALL                  --> press 6"

        while True:
            usr_input = raw_input("Your selection: ")
            if usr_input == "1" or usr_input == "2" or usr_input == "3" or usr_input == "4" or usr_input == "5" or usr_input == "6":
                break
            else:
                print "bad input, try again"

        if usr_input == "1":
            self.from_kuaidaili()
        if usr_input == "2":
            self.from_proxy360()
        if usr_input == "3":
            self.from_66ip()
        if usr_input == "4":
            self.from_nianshao()
        if usr_input == "5":
            self.from_mimvp()
        if usr_input == "6":
            self.from_kuaidaili()
            self.from_proxy360()
            self.from_66ip()
            self.from_mimvp()
            self.from_nianshao()


    def ip_check(self):

        LENGTH, COUNT, FOUND = len(self.valid_ips), 1, 0

        print 'performing final checks'

        for ip in self.valid_ips:
            ranges = {'gkcanpoint': '0', 'zkcanpoint': '0', 'dearedu': '0', 'ht88': '0',
            'tl100': '0', 'xiangpi': '0', 'daliankao': '0', 'ks5u': '0', 'hengqian': '0',
            'jb1000': '0', 'jtyhjyGaozhong': '0', 'twentyOneCnjy': '0', 'xueyou': '0','ziyuanku': '0'}
            SCOUNT = 0
            print '-----------------------------------------------'
            for sites in self.objectives.keys():
                try:
                    self.url_user_agent(ip, self.objectives[sites], 5)
                    ranges[sites] = '1'
                    SCOUNT += 1
                    print sites + ' successfully opened'
                except Exception, e:
                    print sites + '------>'+str(e)

            found_ip = {'IP': ip.split(':')[0], 'PORT': ip.split(':')[1], 'Range': ranges,
            'Date': datetime.today().strftime('%Y-%m-%d'), 'Successrate': str((SCOUNT/float(14))*100)}

            if SCOUNT > 3 and self.collection.find_one(found_ip) == None: #keep only if we have 4 or more valid ips
                self.collection.insert_one(found_ip)
                FOUND += 1
                print 'inserted {}, proxy accessible to.. \n {}'.format(ip, found_ip)

            print str(COUNT) + "/" + str(LENGTH)
            COUNT += 1
            print '-----------------------------------------------'

        print str(FOUND) +  ' ips added to collection'


if __name__ == "__main__":
    ip_get = get_ip()
    ip_get.run_friendly()
    ip_get.ip_check()
