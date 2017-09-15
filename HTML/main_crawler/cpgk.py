# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
import pymongo, sys, urllib2, urllib, time, cookielib, os, re, platform, json, requests, random, time, traceback, logging
from datetime import datetime
from tools import dateformat, get_grade, get_area
from collections import defaultdict
from random import choice

reload(sys)
sys.setdefaultencoding('utf8')

class conf:
    mongo_ip = '127.0.0.1'
    mongo_port = 27017
    subjects = [ "数学", "物理", "地理", "化学", "历史", "语文", "政治", "英语", "生物", "科学" ]

class cpgk:

    def __init__(self):
        mc = pymongo.MongoClient(conf.mongo_ip, conf.mongo_port)
        logfile = '/opt/spider/logs/canpoint.log'
        logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
        self.canpoint = mc.spider.canpoint
        self.download_user = ''
        self.download_user_status = False
        self.user_login_status = False
        self.user_point = 0
        self.download_urls = defaultdict(list)
        self.gc_extractor = get_grade.grade()
        self.pcc_extractor = get_area.pcc_area()

    def login(self):
        if self.download_user == '' or self.download_user_status == False:
            while True:
                register_status, username = self.register()
                if register_status:
                    self.download_user = username
                    self.download_user_status = True
                    self.user_login_status = False
                    # system defatul add 10 point
                    self.user_point = 10
        if self.login_status == False:
            # .... edit login script

            self.cj = cookielib.CookieJar()
            self.mySession = requests.session()
            self.mySession.headers.update({'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})
            res = self.mySession.get('http://gk.canpoint.cn/login/loginuser.ashx?ln='+self.download_user+'&lp=1234qwer&cp=0', cookies = self.cj)

            self.user_login_status = True

    def download(self, res_id):
        #login shoudl be supplied
        download_url = 'http://gk.canpoint.cn/DownFile.aspx'

        try:
            response = self.mySession.post('http://gk.canpoint.cn/DownFile.aspx', data={'docid': res_id}, cookies=self.cj)
            if 'Content-Disposition' not in response.headers:

                if u'您不是VIP用户,不允许下载4星和顶级资料' in response.text:
                    print '{} is a VIP only document. Robot cannot download.'.format(res_id)
                    return
                elif u'每天下载上限为50' in response.text:
                    print 'robot {} is exhausted. trying with a new one'.format(self.download_user)
                    self.cj.clear()
                    self.mySession.close()
                    self.login()
                    self.download(res_id)
                    return
                elif u'你的剩余积分不足' in response.text:
                    print 'robot points is too low. robot hp is probably corrupt. RESET HP TO 0'
                    self.cj.clear()
                    self.mySession.close()
                    self.login()
                    self.download(res_id)
                    return
                else:
                    print 'unknown error, terminating process'
                    print response.text
                    quit()

            extension = tools.get_extension(response.headers['Content-Disposition'])
            filename = '{}.{}'.format(res_id, extension)
            filepath = '/www/api/file/cpgk/{}/{}/{}'.format(date[0], date[1], filename)

            if self.mkdir(filepath):
                with open(filepath, 'wb') as f:
                    f.write(response.content)

        except Exception, e:
            print e

    def mkdir(self, filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
                return True
            except:
                print 'mkdir error:', filepath
                return False

    # register
    # return login_status & username
    def register(self):
        name = 'wsxedc%06d' % random.randint(0, 999999)
        print 'register', name
        post_data = {
            'ddl_szsf$UpdateManager1': 'ddl_szsf$UpdatePanel1|ddl_szsf$city',
            'txt_loginname': name, 'txt_realname':	"Jack",
            'txt_loginpassword': "1234qwer", 'txt_loginpassword1': "1234qwer", 'txt_pwquestion': "1234", 'txt_pwanswer':	"qwer",
            'ddl_sex': "1", 'txt_birthday': "", 'txt_mail':	name + "@123.com",
            'ddl_szsf$province': "1", 'ddl_szsf$city': "东城区",
            'txtuserjob': "教师", 'txtschoolType': "小学", 'ddl_isseniorteacher': "", 'ddl_subject': "语文", 'txt_workplace': "北京四中",
            'txt_mobile': "13012345678", 'txt_telephone': "", 'txt_qq': "", 'txt_address': "", 'txt_zip': "",
            'txt_job': "", 'textarea': "全品教学网+用户注册协议\r\n\r\n一．用户\r\n1…15.3本协议的解释权归全品教学网所有。\r\n\r\n",
            'app': "on", 'btn_save': "提交", 'XXZC': '',
            '__EVENTTARGET': 'ddl_szsf$city', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__ASYNCPOST': 'true',
            '__VIEWSTATE': '/wEPDwUIODgwOTU5MTgPZBYCAgEPZBYGAgEPFgIeCWlubmVyaHRtbAXgEjxsaW5rIGhyZWY9ImNzcy9jYW4uY3NzIiByZWw9InN0eWxlc2hlZXQiIHR5cGU9InRleHQvY3NzIiAvPg0KPGxpbmsgaHJlZj0iY3NzL3N0eWxlXzIwMDkuY3NzIiByZWw9InN0eWxlc2hlZXQiIHR5cGU9InRleHQvY3NzIiAvPg0KPHRhYmxlIHdpZHRoPSIxMDA0IiBib3JkZXI9IjAiIGNlbGxwYWRkaW5nPSIwIiBjZWxsc3BhY2luZz0iMCIgY2xhc3M9ImJqIj4NCiAgICA8dHI+DQogICAgICAgIDx0ZCB3aWR0aD0iMjkiPg0KICAgICAgICAgICAgJm5ic3A7DQogICAgICAgIDwvdGQ+DQogICAgICAgIDx0ZCB3aWR0aD0iMjM0Ij4NCiAgICAgICAgICAgIDxhIGhyZWY9Imh0dHA6Ly93d3cuY2FucG9pbnQuY24vIj4NCiAgICAgICAgICAgICAgICA8aW1nIHNyYz0iaW1hZ2VzL2xvZ28uanBnIiB3aWR0aD0iMjA0IiBoZWlnaHQ9IjEwNSIgYm9yZGVyPSIwIiAvPjwvYT4NCiAgICAgICAgPC90ZD4NCiAgICAgICAgPHRkIHdpZHRoPSIxNjMiPg0KICAgICAgICAgICAgPGEgaHJlZj0iaHR0cDovL2drLmNhbnBvaW50LmNuLyI+DQogICAgICAgICAgICAgICAgPGltZyBzcmM9ImltYWdlcy9nei5qcGciIHdpZHRoPSIxNjMiIGhlaWdodD0iMTA1IiBib3JkZXI9IjAiIC8+PC9hPg0KICAgICAgICA8L3RkPg0KICAgICAgICA8dGQgd2lkdGg9IjE3Ij4NCiAgICAgICAgICAgIDxpbWcgc3JjPSJpbWFnZXMveC5qcGciIHdpZHRoPSI1IiBoZWlnaHQ9IjEwNSIgLz4NCiAgICAgICAgPC90ZD4NCiAgICAgICAgPHRkIHdpZHRoPSIxNjMiPg0KICAgICAgICAgICAgPGEgaHJlZj0iaHR0cDovL3prLmNhbnBvaW50LmNuLyI+DQogICAgICAgICAgICAgICAgPGltZyBzcmM9ImltYWdlcy9jei5qcGciIHdpZHRoPSIxNjIiIGhlaWdodD0iMTA1IiBib3JkZXI9IjAiIC8+PC9hPg0KICAgICAgICA8L3RkPg0KICAgICAgICA8dGQgd2lkdGg9IjE3Ij4NCiAgICAgICAgICAgIDxpbWcgc3JjPSJpbWFnZXMveC5qcGciIHdpZHRoPSI1IiBoZWlnaHQ9IjEwNSIgLz4NCiAgICAgICAgPC90ZD4NCiAgICAgICAgPCEtLSA8dGQgd2lkdGg9IjUwIj48YSBocmVmPSJodHRwOi8vZ3p0LmNhbnBvaW50LmNuL2xvZ2luLmFjdGlvbj91c2VyaWQ9Jm1rPTlBMUI0RTY2NTFGNjYxNzRFM0MyQkYxNzRDNzAwMzM1Ij48aW1nIHNyYz0iaW1hZ2VzMjAwOC9iLmdpZiIgICB3aWR0aD0iMTYiIGhlaWdodD0iMTA1IiBib3JkZXI9IjAiIC8+PC9hPjwvdGQ+LS0+DQogICAgICAgIDx0ZCB3aWR0aD0iMTYzIj4NCiAgICAgICAgICAgIDwhLS08YSBocmVmPSJodHRwOi8vd3d3LmNhbnBvaW50LmNuL2dvZ3p0LmFzcHgiPg0KICAgICAgICAgICAgICAgIDxpbWcgc3JjPSJpbWFnZXMvZ2t0LmpwZyIgaGVpZ2h0PSIxMDUiIGJvcmRlcj0iMCIgd2lkdGg9IjE2MiIgLz48L2E+LS0+DQogICAgICAgICAgICA8IS0tIDxhIGhyZWY9Imh0dHA6Ly94eC5jYW5wb2ludC5jbi8iPg0KICAgICAgICAgICAgICAgIDxpbWcgc3JjPSJpbWFnZXMveHguanBnIiBoZWlnaHQ9IjEwNSIgYm9yZGVyPSIwIiB3aWR0aD0iMTYyIiAvPjwvYT4tLT4NCiAgICAgICAgICAgIDxhIGhyZWY9Imh0dHA6Ly93d3cuY2FucG9pbnQubmV0LyI+DQogICAgICAgICAgICAgICAgPGltZyBzcmM9ImltYWdlcy/lhajlk4Fsb2dvLTA2MTQucG5nIiBoZWlnaHQ9IjEwNSIgYm9yZGVyPSIwIiB3aWR0aD0iMTYyIiAvPjwvYT4NCiAgICAgICAgPC90ZD4NCiAgICAgICAgPCEtLXRkIHdpZHRoPSIxMiI+PGltZyBzcmM9ImltYWdlcy94LmpwZyIgd2lkdGg9IjUiIGhlaWdodD0iMTA1IiAv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c29saWQ7DQogICAgYmFja2dyb3VuZDogIzQ0NDQ0NDsiPg0KICAgIDx0cj4NCiAgICAgICAgPHRkIGFsaWduPSJjZW50ZXIiPg0KICAgICAgICAgICAgPGJyPg0KICAgICAgICAgICAgPHAgaWQ9InNpXzIiIHN0eWxlPSJwYWRkaW5nOiAwOyI+DQogICAgICAgICAgICAgICAgPGEgaHJlZj0iaHR0cDovL2drLmNhbnBvaW50LmNuL2d1aWRlLmFzcHg/Y29udGVudD1oZWxwQ29udGVudF9tYWluIj7mlrDmiYvkuIrot688L2E+IDxhIGhyZWY9Imh0dHA6Ly9nay5jYW5wb2ludC5jbi91c2VydXBsb2FkLmFzcHgiPg0KICAgICAgICAgICAgICAgICAgICDotYTmlpnkuIrkvKA8L2E+IDxhIGhyZWY9Imh0dHA6Ly9nay5jYW5wb2ludC5jbi9kZWNsYXJlLmFzcHgiPueJiOadg+WPiuWFjei0o+WjsOaYjjwvYT4gPGEgaHJlZj0ibWFpbHRvOmNhbnBvaW50QDEyNi5jb20iPg0KICAgICAgICAgICAgICAgICAgICAgICAg6IGU57O75oiR5LusPC9hPiA8YSBocmVmPSJodHRwOi8vZ2suY2FucG9pbnQuY24vbWVzc2FnZS5hc3B4Ij7nlZnoqIDmnb88L2E+PC9wPg0KICAgICAgICAgICAgPHAgaWQ9InNpXzMiIHN0eWxlPSJwYWRkaW5nOiAwOyBjb2xvcjogI2ZmZjsgbWFyZ2luOiA1cHggMCAzcHggMDsiPg0KICAgICAgICAgICAgICAgIDxmb250IGNvbG9yPSJ3aGl0ZSI+MDEwLTU3NDc5NTkyIHwgMDEwLTU3NDc5NTkzICA8L2ZvbnQ+Jm5ic3A7Jm5ic3A75LqsSUNQ5aSHPGEgaHJlZj0iaHR0cDovL3d3dy5taWliZWlhbi5nb3YuY24iPjEwMDMyNTczPC9hPiZuYnNwOw0KICAgICAgICAgICAgICAgIEUtbWFpbO+8mjxhIGhyZWY9Im1haWx0bzpqaWFveHVlQGNhbnBvaW50LmNuIj5qaWFveHVlQGNhbnBvaW50LmNuPC9hPiZuYnNwOw0KICAgICAgICAgICAgPC9wPg0KICAgICAgICA8L3RkPg0KICAgIDwvdHI+DQo8L3RhYmxlPg0KPGxpbmsgaHJlZj0iY3NzL3N0YW5kYXJzLmNzcyIgcmVsPSJzdHlsZXNoZWV0IiB0eXBlPSJ0ZXh0L2NzcyIgLz4NCjxsaW5rIGhyZWY9ImNzcy9zaGFyZS5jc3MiIHJlbD0ic3R5bGVzaGVldCIgdHlwZT0idGV4dC9jc3MiIC8+DQpkZA=='
        }
        headers = {
            'Host': 'www.canpoint.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://www.canpoint.cn/Register.aspx'
        }
        req = urllib2.Request(
            url = 'http://www.canpoint.cn/Register.aspx',
            headers = headers,
            data = urllib.urlencode(post_data)
        )
        op = urllib2.urlopen(req)
        return  '1|#||4|15|pageRedirect||%2fDefault.aspx|' in unicode(op.read(), 'utf-8'), name

    # gather base info
    def get_base_info(self, page):
        '''
        retrieves all the meta-data from http://gk.canpoint.cn/WebService/qpService.asmx/getSearchTable
        needed to read the actual download url as it is encrypted
        '''
        post_data = {
            'key':'',
            'type':'',
            'areaid':'',
            'subcataid':'',
            'maincataid':'',
            'mscataid':'',
            'editionid':'',
            'bookcataid':'',
            'cellcataid':'',
            'lessonid':'',
            'indexPage':'%d' % page,
            'stype':'1',
            'keytype':'1'
        }
        headers = {
            'Content-Type': 'application/json'
        }
        request = urllib2.Request(
            url = 'http://gk.canpoint.cn/WebService/qpService.asmx/getSearchTable',
            headers = headers,
            data = json.dumps(post_data)
        )
        f = urllib2.urlopen(request)
        js = unicode(f.read(), 'utf8')
        d = json.loads(str(js))['d']
        js_data = json.loads('[%s]' % str(d))[0]['Table']['Table']
        data = []
        for d in js_data:
            info = [d['id'], d['title'], int(d['point']), int(d['downtimes'])]
            data.append(info)
            print info
        return data

    def insert_document(self, meta_data):

        try:
            url = 'http://gk.canpoint.cn/FileDetail-%s.html' % meta_data[0]
            html = unicode(urllib2.urlopen(url).read(), 'utf-8')
            d = pq(html)
            res_title, res_point = meta_data[1], meta_data[2]
            (res_province, res_city, res_county) = self.pcc_extractor.extraction(res_title)
            (res_grade, res_class) = self.gc_extractor.extraction(res_title, '', '')
            description = d('.tb_down tr').eq(2)('td').eq(1).text().split()
            res_subject = description[0]
            res_date = dateformat.format_date(d('.tb_down tr').eq(1).find('td').eq(3).text().strip())
            res_intro = d('div.des_down').html().split('<br />')[-1].strip()
            crawl_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            #TODO res_version, res_type
            res_version, res_type = '', ''

            document = {'res_title': res_title, 'res_url': url, 'res_date': res_date, 'res_downcount': meta_data[3],
                        'res_point': res_point, 'res_subject': res_subject, 'res_type': res_type, 'res_grade': u'高中',
                        'res_intro': res_intro, 'res_class': res_class, 'res_version': res_version,
                        'res_province': res_province, 'res_city': res_city, 'res_county': res_county, 'res_id':  meta_data[0],
                        'res_file': '', 'site_id': 'canpoint', 'date': crawl_date}
            if (res_point <= 10) and (res_point >= 0):
                self.download_urls[res_point].append(meta_data[0])
            print res_title, url
            #self.canpoint.insert_one(document)

        except Exception, e:
            print e
            logging.info('error at {}, reason {}'.format(meta_data[0], traceback.format_exc()))


    # run new
    def gather(self):
        page = 1
        over = False
        error_count = 0
        while True:
            data = self.get_base_info(page)
            for meta_data in data:                                                      #read all the meta-data per page
                r_id = meta_data[0]
                if self.canpoint.count({'res_id': r_id}) > 0:            #find duplicates? ignore. maybe just small fault
                    print 'error'
                    error_count += 1
                    break                                                       #evaluate
                #at this point url does not exist in colleciton so we can insert it into database
                #self.canpoint.save(o)                                          #if it passes checking we get detailed info
                self.insert_document(meta_data)
                # reource download
                #self.download(o['res_id'])
            if error_count > 10:                                                #10 duplicates? we msut have hit the end of new data
                break
            page += 1
        print 'run new over'

    def run(self):
        self.gather()

# 注册 --> 登陆 --> 抓信息 --> 判断数据库是否存在(超过10次跳出子任务) --> 直接下载 --> 直到用户不能下载 --> 再次注册 --> 继续抓信息 --> 下载
if __name__ == '__main__':
    c = cpgk()
    c.gather()
