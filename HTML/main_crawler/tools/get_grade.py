# -*- coding: utf-8 -*-
import pymongo, sys

sys.path.insert(0, '/opt/git/Spider/src/')
from data import conf


class grade:

    '''
    Tool that finds res_class from some string, and attempts to format it
    to match our desired format
    '''

    def __init__(self):

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.collection = client.config.grade
        self.class_dict = {1: u'一年级', 2: u'二年级', 3: u'三年级', 4: u'四年级', 5: u'五年级', 6: u'六年级', 7: u'七年级',
        8: u'八年级', 9: u'九年级', 10: u'高一', 11: u'高二', 12: u'高三'}
        self.MDICT = {}

        w = ''
        for doc in self.collection.find():
            name = doc['name']
            point = doc['ordinal']
            for c in name[:-1]:
                w += c
                self.MDICT[w] = '*'
            self.MDICT[name] = point
            w = ''
            if 'otherName' in doc:
                otherName = doc['otherName'].split()
                for oNames in otherName:
                    for c in oNames[:-1]:
                        w += c
                        self.MDICT[w] = '*'
                    self.MDICT[oNames] = point
                    w = ''


    def extraction(self, title, res_grade, res_class):

        '''
        Function first extracts from res_class from res_class obtained from
        crawled webpage. if webpage res_class cannot be formatted, it then extracts
        from the title. if res_class is obtained, res_grade is automatically added.
        If res_class cannot be obtained, function returns the original res_class
        passed into it
        '''

        def extractor(datastring):
            word, memo = '', None
            success = []
            for w in datastring:
                word += w
                if word in self.MDICT:
                    if self.MDICT[word] == '*':
                        continue
                    else:
                        ordinal = self.MDICT[word]
                        if ordinal < 7:
                            return (u'小学', self.class_dict[ordinal])
                        elif ordinal > 9:
                            return (u'高中', self.class_dict[ordinal])
                        else:
                            return (u'初中', self.class_dict[ordinal])
                if word not in self.MDICT:
                    word = ''
            return (res_grade, res_class)

        rc_copy = res_class
        data = extractor(res_class)
        (res_grade, res_class) = data
        if (res_class == rc_copy) and rc_copy not in self.class_dict.values():
            res_class = ''
            return extractor(title)
        else:
            return data




if __name__ == "__main__":
    grade = grade()
    xx = grade.extraction(u'2017年上海市春季高考数学试卷+word版无答案', '', u'九年级')
    print 'grade: ', xx[0]
    print 'class: ', xx[1]
