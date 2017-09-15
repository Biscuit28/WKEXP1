# -*- coding: utf-8 -*-
import pymongo
from datetime import *


class filter:

    def __init__(self):

        self.AREAS = set([u'北京',u'天津',u'上海',u'重庆',u'河北',u'辽宁',u'黑龙江',u'吉林',u'山东',u'山西',u'安徽',
        u'浙江',u'江苏',u'江西',u'广东',u'福建',u'海南',u'河南',u'湖北',u'湖南',u'四川',u'云南',u'贵州',
        u'陕西',u'甘肃',u'青海',u'宁夏',u'内蒙古',u'广西',u'西藏', u'新疆', u'香港',u'澳门', u'台湾'])

        self.SUBJECTS = set([u'数学', u'英语', u'语文', u'物理', u'化学', u'地理', u'生物', u'政治', u'信息技术',
         u'品德', u'音乐', u'科学', u'美术', u'体育'])

        self.CITIES = set([u'阿坝',u'阿拉善',u'安顺',u'鞍山',u'巴彦淖尔',u'巴中',u'白银',u'百色',
        u'包头',u'保山',u'北海',u'本溪',u'毕节',u'滨州',u'长春',u'长沙',u'常德',u'常州',
        u'朝阳',u'潮州',u'郴州',u'成都',u'赤峰',u'崇左',u'楚雄',u'达州',u'大理',u'大连',
        u'大庆',u'大兴安岭',u'丹东',u'德宏',u'德阳',u'德州',u'迪庆',u'定西',u'东莞',u'东营',
        u'鄂尔多斯',u'鄂州',u'恩施',u'防城港',u'佛山',u'福州',u'抚顺',u'抚州',u'阜新',u'甘南',
        u'甘孜',u'广安',u'广元',u'广州',u'贵安新区',u'贵港',u'贵阳',u'桂林',u'哈尔滨',u'杭州',
        u'河池',u'河源',u'菏泽',u'贺州',u'鹤岗',u'黑河',u'衡阳',u'红河',u'呼和浩特',u'呼伦贝尔',
        u'湖州',u'葫芦岛',u'怀化',u'淮安',u'黄冈',u'黄石',u'惠州',u'鸡西',u'济南',u'济宁',u'佳木斯',
        u'嘉兴',u'嘉峪关',u'江门',u'揭阳',u'金昌',u'金华',u'锦州',u'荆门',u'荆州',u'酒泉',
        u'昆明',u'来宾',u'莱芜',u'兰州',u'乐山',u'丽江',u'丽水',u'连云港',u'凉山',u'辽阳',
        u'聊城',u'临沧',u'临夏',u'临沂',u'柳州',u'六盘水',u'龙岩',u'陇南',u'娄底',u'泸州',
        u'茂名',u'眉山',u'梅州',u'绵阳',u'牡丹江',u'内江',u'南昌',u'南充',u'南京',u'南宁',
        u'南平',u'南通',u'宁波',u'宁德',u'怒江傈',u'攀枝花',u'盘锦',u'平凉',u'莆田',u'普洱',u'七台河',u'齐齐哈尔',
        u'潜江',u'黔东南',u'黔南',u'黔西南',u'钦州',u'青岛',u'清远',u'庆阳',u'曲靖',u'衢州',
        u'泉州',u'日照',u'三明',u'汕头',u'汕尾',u'韶关',u'邵阳',u'绍兴',u'深圳',u'神农架',
        u'沈阳',u'十堰',u'双鸭山',u'思茅',u'苏州',u'宿迁',u'绥化',u'随州',u'遂宁',u'台州',
        u'泰安',u'泰州',u'天门',u'天水',u'铁岭',u'通辽',u'铜仁',u'威海',u'潍坊',u'温州',
        u'文山',u'乌海',u'乌兰察布',u'乌鲁木齐',u'无锡',u'梧州',u'武汉',u'武威',u'西宁',
        u'西双版纳',u'锡林郭勒',u'厦门',u'仙桃',u'咸宁',u'湘潭',u'湘西',u'襄阳',u'孝感',
        u'兴安',u'徐州',u'雅安',u'烟台',u'盐城',u'扬州',u'阳江',u'伊春',u'宜宾',u'宜昌',
        u'益阳',u'营口',u'永州',u'玉林',u'玉溪',u'岳阳',u'云浮',u'枣庄',u'湛江',u'张家界',
        u'张掖',u'漳州',u'昭通',u'肇庆',u'镇江',u'中山',u'舟山',u'株洲',u'珠海',u'资阳',u'淄博',
        u'自贡',u'遵义'])

        self.KEYWORDS = ''


    def keywords(self):

        KEYWORDS = set()

        def construct_keywords(KEYWORD, List):

            for words in List:
                temp_word = ''
                for characters in words[:-1]:
                    temp_word = temp_word + characters
                    KEYWORD.add(temp_word)

            return KEYWORDS

        KEYWORDS = construct_keywords(KEYWORDS, self.AREAS)
        KEYWORDS = construct_keywords(KEYWORDS, self.SUBJECTS)
        KEYWORDS = construct_keywords(KEYWORDS, self.CITIES)

        return KEYWORDS


    def state_machine(self, title):

        LISTEN_STATE, CHECK_STATE = True, False
        area, subject, city, word = '', '', '', ''

        for char in title:
            if LISTEN_STATE:
                if char in self.KEYWORDS:
                    LISTEN_STATE, CHECK_STATE = False, True
            if CHECK_STATE:
                word = word + char
                if word not in self.KEYWORDS:
                    if word in self.AREAS:
                        area = word
                    elif word in self.SUBJECTS:
                        subject = word
                    elif word in self.CITIES:
                        city = word
                    else:
                        pass

                    LISTEN_STATE, CHECK_STATE = True, False
                    word = ''

        return (area, subject, city)


    def filter(self, host='10.1.1.13', port = 27017):

        time_start = datetime.today()
        #first get the mongoDB ready
        client = pymongo.MongoClient(host, port)
        collection = client.spider.similar

        DIFFCOUNT, LOOP_COUNT = 0, 0

        self.KEYWORDS = self.keywords()

        for doc in collection.find({'x_title': {'$exists': 1}}):

            same = 1
            x_title = doc["x_title"]
            o_title = doc["o_title"]
            id = doc["_id"]
            x_res = self.state_machine(x_title)
            o_res = self.state_machine(o_title)

            if x_res[0] != o_res[0] and (x_res[0] != '' and o_res[0] != ''):
                same = 0
                DIFFCOUNT += 1
                print 'NOT SIMILAR'
                print 'x_title: ' + x_title + '\n' + 'o_title: ' + o_title + '\n' + 'difference (area): ' + x_res[0] + '<-->' + o_res[0]
            if x_res[1] != o_res[1] and (x_res[1] != '' and o_res[1] != ''):
                same = 0
                DIFFCOUNT += 1
                print 'NOT SIMILAR'
                print 'x_title: ' + x_title + '\n' + 'o_title: ' + o_title + '\n' + 'difference (subject): ' + x_res[1] + '<-->' + o_res[1]
            if x_res[2] != o_res[2] and (x_res[2] != '' and o_res[2] != ''):
                same = 0
                DIFFCOUNT += 1
                print 'NOT SIMILAR'
                print 'x_title: ' + x_title + '\n' + 'o_title: ' + o_title + '\n' + 'difference: (city) ' + x_res[2] + '<-->' + o_res[2]

            LOOP_COUNT += 1
            #now we can add to mongodb

            #collection.find({'$and' {"x_title": {"$exists": 1}}, {"sim": {"exists": 0}}})

        time_diff = datetime.today() - time_start
        print 'found {} different items. \n Total runtime {} items in {} seconds'.format(DIFFCOUNT, LOOP_COUNT, time_diff.total_seconds())


if __name__ == "__main__":

    f = filter()
    f.filter()
    # f.KEYWORDS = f.keywords()
    # f.state_machine(u'2017年江苏省南京市中考语文试卷（解析版)')
    # f.state_machine(u'2017年江苏省南京市栖霞区中考模拟语文试卷（二）')


    #
