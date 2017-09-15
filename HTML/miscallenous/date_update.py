import pymongo
from date_format import format_date

client = pymongo.MongoClient('10.1.1.13', 27017)

canpoint = client.spider.canpoint                                               #DONE
daliankao =client.spider.daliankao                                              #DONE
dearedu = client.spider.dearedu                                                 #DONE
hengqian = client.spider.hengqian                                               #DONE
ht88 =client.spider.ht88                                                        #DONE
jb1000 = client.spider.jb1000                                                   #DONE
jtyhjyGaozhong = client.spider.jtyhjyGaozhong                                   #DONE
tl100 = client.spider.tl100                                                     #DONE
twentyOne = client.spider.twentyOne                                             #DONE
xiangpi = client.spider.xiangpi                                                 #DONE
xueyou = client.spider.xueyou                                                   #DONE
ziyuanku = client.spider.ziyuanku                                               #DONE *
zk5u = client.spider.zk5u                                                       #DONE
ks750 = client.spider.ks750                                                     #DONE
ks5u = client.spider.ks5u


def update(col):

    COUNT = 0

    print col.count()

    for doc in col.find({"res_date" : {'$exists': 1}}):
        COUNT += 1
        print COUNT
        docid = doc["_id"]
        print docid
        new_date = format_date(doc["res_date"])
        doc["res_date"] = new_date
        print new_date
        col.update({'_id': docid}, {"$set": doc}, upsert=False)


def tmp(col):

    COUNT = 0

    print col.count()

    for doc in col.find({"date" : {'$exists': 1}}):
        print doc['date']
        print format_date(doc['date'])
        # COUNT += 1
        # print COUNT
        docid = doc["_id"]

        #new_date = format_date(doc["res_date"])
        doc["res_date"] = format_date(doc['date'])
        # print new_date
        col.update({'_id': docid}, {"$set": doc}, upsert=False)

tmp(zk5u)
