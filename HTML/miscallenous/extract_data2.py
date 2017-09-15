# -*- coding: utf-8 -*-
import pymongo
from datetime import *
from time import sleep
from collections import defaultdict
from master_dict import summon_dict

#create the set
client = pymongo.MongoClient('10.1.1.13', 27017)
collection_list = [client.config.province, client.config.city, client.config.county]


def get_set(collections, create_dict=False):

    important_list = []
    master_dict = {}
    large_set = set()
    COUNT = 0
    category = ''
    for collection in collections:
        COUNT += 1
        for doc in collection.find():
            longName = doc['name']
            shortName = doc['shortName']

            if create_dict:
                if COUNT == 1: #province, get ID
                    ID = doc['id']
                    category = 'res_province'

                if COUNT == 2: #city, get ID
                    ID = doc['parentId']
                    category = 'res_city'

                if COUNT == 3: #county
                    sub_ID = doc['parentId']
                    tmp = collections[1].find_one({'id': sub_ID})
                    ID = tmp['parentId']
                    category = 'res_county'

                master_dict[longName] = [ID, category, longName]
                master_dict[shortName] = [ID, category, longName]

            important_list.append(longName)
            important_list.append(shortName)

    for word in important_list:
        w = ''
        for chars in word:
            w += chars
            if w == word:
                large_set.add(w+'*')
            else:
                large_set.add(w)
    return (large_set, master_dict)


def sort_and_check(succ):

    ele_dict = defaultdict(list)
    res_province, res_city, res_county = '', '', ''

    for name in succ:

        data = MDICT[name]
        ID = data[0]
        full_name = data[2]
        category = data[1]
        ele_dict[ID].append([category, full_name])

    if ele_dict:
        selected_id = max(ele_dict.iterkeys(), key = (lambda key: len(ele_dict[key])))

        for ele in ele_dict[selected_id]:
            if ele[0] == 'res_province':
                res_province = ele[1]
            if ele[0] == 'res_city':
                res_city = ele[1]
            if ele[0] == 'res_county':
                res_county = ele[1]

    return (res_province, res_city, res_county)


def extraction(title):

    word, memo = '', None
    success = []

    for w in title:
        word += w
        if memo != None:
            if (word+'*'in LSET) or (word in LSET):
                memo = None
            else:
                success.append(memo)
                memo = None
                word = word[-1]
        if word+'*' in LSET:
            memo = word
            continue
        if word not in LSET and memo == None:
            word = ''

    return sort_and_check(success)


def update_whole():

    targets = [client.spider.canpoint, client.spider.daliankao, client.spider.dearedu, client.spider.hengqian,
    client.spider.ht88, client.spider.jb1000, client.spider.jtyhjyGaozhong, client.spider.ks5u,
    client.spider.ks750, client.spider.tl100, client.spider.twentyOne, client.spider.xiangpi,
    client.spider.xueyou, client.spider.ziyuanku, client.spider.zk5u]

    start = datetime.today()

    COUNT = 0

    for col in targets:
        for ele in col.find():
            title = ele['res_title']
            doc_id = ele['_id']
            print title
            (res_province, res_city, res_county) = extraction(title)
            ele['res_province'] = res_province
            ele['res_county'] = res_county
            ele['res_city'] = res_city
            col.update_one({'_id': doc_id}, {"$set": ele}, upsert = False)
            COUNT += 1

    print datetime.today() - start
    print 'updated', COUNT, 'values'


DATA = get_set(collection_list)
LSET = DATA[0]
MDICT = summon_dict()


if __name__ == '__main__':
    update_whole()
