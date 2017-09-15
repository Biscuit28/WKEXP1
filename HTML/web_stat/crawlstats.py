# -*- coding: utf-8 -*-
import pymongo, traceback, sys, pprint, re
from datetime import datetime, timedelta
sys.path.insert(0, '/opt/git/Spider/src/')
from data import conf
sys.path.insert(0, '/opt/git/Spider/src/gather/tools')
import dateformat




class spider_stats:

    '''
    DESCRIPTION: Calculates and collects statistics from spider database

    '''

    def __init__(self):

        self.client = pymongo.MongoClient('localhost', 27017)
        self.subjectlist = [u'语文', u'数学', u'英语', u'物理', u'化学', u'生物',
                                u'政治', u'历史', u'地理']
        self.collection = self.client.spider.res
        self.provdict = {0: u'全部的', 1: u'北京', 2: u'天津', 3: u'河北', 4: u'山西', 5: u'内蒙古',
            6: u'辽宁', 7: u'吉林', 8: u'黑龙江', 9: u'上海', 10: u'江苏', 11: u'浙江',
            12: u'安徽', 13: u'福建', 14: u'江西', 15: u'山东', 16: u'河南', 17: u'湖北',
            18: u'湖南', 19: u'广东', 20: u'广西', 21: u'海南', 22: u'重庆', 23: u'四川',
            24: u'贵州', 25: u'云南', 26: u'西藏', 27: u'陕西', 28: u'甘肃', 29: u'青海',
            30: u'宁夏', 31: u'新疆', 32: u'台湾', 33: u'香港', 34: u'澳门'}
        self.site_translations = {'zxxk': u'学科网', 'dearedu':u'第二教育网', 'twentyOne': u'21世纪教育网', 'ziyuanku': u'中华资源库'}



    def update_stat_col(self):

        '''
        takes the res collection and creates stat on how many documents uploaded
        by each site, for all subjects, everyday. ie,

        {'res_date': 2017, 'zxxk': {'subject1': 12, 'subject2': 234, 'total': 246},
        'dearedu': {'subject1': 2, 'subject2':  14, 'total': 16},
        'canpoint': {'subject1': 42, 'subject2':  101, 'total': 143} ....
        '''

        projector = {"$project": {
            "date": {"$substr": ["$res_date", 0, 10]},
            "site_id": 1,
            "res_subject": 1,
            "res_province": 1,
        }}

        first_grouper = {"$group": {
            "_id": {
                    "date": "$date",
                    "subject": "$res_subject",
                    "site": "$site_id"
                    },
            "count": {"$sum": 1}
            }
        }

        second_grouper = {"$group": {                                           #second grouping is there to group all the different subjects from first grouping
            "_id": "$_id.date",                                                 #under each date
            "site_name": {
                "$push": {
                    "site": "$_id.site",
                    "subject": "$_id.subject",
                    "count": "$count"
                },
            },
            "total": {"$sum": "$count"}
          }
        }

        PIPELINE = [projector, first_grouper, second_grouper]
        aggregate_result = list(self.collection.aggregate(PIPELINE))
        ready_list = sorted(list(aggregate_result), key=lambda k: k['_id'])
        copy_list = ready_list[:]

        for dicts in copy_list:
            d_date = dicts['_id']
            if dateformat.compare_date(d_date, '2017-01-01'):
                ready_list.remove(dicts)

        pprint.pprint(ready_list)

        START_DATE = datetime.strptime('2017-01-01 23:59:59', "%Y-%m-%d %H:%M:%S")
        START_DATE = datetime.strptime('2017-01-01 23:59:59', "%Y-%m-%d %H:%M:%S")
        END_DATE = datetime.today()

        #beautify list created from aggregate and insert it to total collection
        stat_collection = self.client.stats.total
        site_total_dict = {}
        index_counter = 0
        while START_DATE < END_DATE:
            collection_date = ready_list[index_counter]['_id']
            start_date_string = START_DATE.strftime('%Y-%m-%d')
            if start_date_string == ready_list[index_counter]['_id']:
                print collection_date
                doc = {'res_date': collection_date}
                TOTAL = 0
                for sub_dict in ready_list[index_counter]['site_name']:
                    try:
                        site_name = sub_dict['site']
                        site_subject= sub_dict['subject']
                        site_count = sub_dict['count']
                    except Exception, e:
                        continue
                    if site_name not in doc:
                        site_total_dict[site_name] = 0
                        doc[site_name] = {}
                    doc[site_name][site_subject] = site_count
                    site_total_dict[site_name] += site_count
                    TOTAL += site_count
                doc['day_total'] = TOTAL
                for skey in site_total_dict.keys():
                    doc[skey]['site_total'] = site_total_dict[skey]
                index_counter += 1
                if stat_collection.find_one({"res_date": start_date_string}):
                    print 'already in collection'
                else:
                    stat_collection.insert_one(doc)
                site_total_dict = {}
            START_DATE += timedelta(days=1)



    def get_subject_stats(self, start, prov_filter):

        '''
        Finds the amount of documents for each of the following subjects for all
        collections between start_date and end_date

        语文 (Chinese) 数学 (Math) 英语 (English) 物理 (Physics) 化学 (Chemistry)
        生物 (Biology) 政治 (Politics) 历史 (History) 地理 (Geography)

        Note* 总计 (Total) means the sum of all documents in each of the above subjects

        '''
        tmps = start
        start += ' 00:00:00'

        end_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S") + timedelta(days=7)
        tmpe = end_date.strftime('%Y-%m-%d')
        end = tmpe + ' 00:00:00'

        subj_list = [u'语文', u'数学', u'英语', u'物理', u'化学', u'生物', u'政治',  u'历史', u'地理']

        PIPELINE = []

        match_list = []
        match_date_cond = {"$and": [{"res_date": {"$gte": start}}, {"res_date": {"$lt": end}}]}
        match_subject_cond = {"$or": [{'res_subject': u'语文'}, {'res_subject': u'数学'}, {'res_subject': u'英语'},
        {'res_subject': u'化学'}, {'res_subject': u'生物'}, {'res_subject': u'政治'}, {'res_subject': u'历史'},
        {'res_subject': u'地理'}]}
        match_site_cond = {"$or": [{'site_id': 'zxxk'},{'site_id': 'dearedu'},{'site_id': 'twentyOne'},{'site_id': 'ziyuanku'}]}
        match_list.append(match_date_cond)
        match_list.append(match_subject_cond)
        match_list.append(match_site_cond)
        if int(prov_filter) != 0:
            match_list.append({'res_province': self.provdict[int(prov_filter)]})
        matcher = {"$match": {"$and": match_list}}                              #matcher matches the condition of the documents we want. ie it filters the documents that we want to group

        first_grouper = {"$group": {                                            #first grouping just creates groups of same site and subject together.
            "_id": {"site": "$site_id",
                    "res_subject": "$res_subject"
                    },
            "subjcount": {"$sum": 1}                                            #coutns how many occurences there are of each group
            }
        }

        second_grouper = {"$group": {                                           #second grouping is there to group all the different subjects from first grouping
            "_id": "$_id.site",                                                 #under each site
            "subjects": {
                "$push": {
                    "subject": "$_id.res_subject",
                    "count": "$subjcount"
                },
            },
            "total": {"$sum": "$subjcount"}
          }
        }
        sorter = {"$sort": {"total": -1}}

        PIPELINE = [matcher, first_grouper, second_grouper, sorter]
        r = list(self.collection.aggregate(PIPELINE))
        #we need something to add to empty
        site_names = ['zxxk', 'twentyOne', 'ziyuanku', 'dearedu']
        result = []
        index = 0
        for s in r:
            result.append([self.site_translations[s['_id']]])
            site_names.remove(s['_id'])
            site_stat = []
            site_dict = {}
            for x in s['subjects']:
                data = x.values()
                site_dict[data[1]] = data[0]
            for subj in subj_list:
                if subj in site_dict.keys():
                    site_stat.append(site_dict[subj])
                else:
                    site_stat.append(0)
            site_stat.append(s['total'])
            result[index] = result[index]+site_stat
            index += 1
        for rsite in site_names:
            result.append([self.site_translations[rsite], 0,0,0,0,0,0,0,0,0,0])


        sdl = tmps.split('-')
        edl = tmpe.split('-')
        TITLE =  u'{}年{}月{}日-{}年{}月{}日 ({})'.format(sdl[0],sdl[1],sdl[2],edl[0],edl[1],edl[2], self.provdict[int(prov_filter)])
        return [end[:-9], TITLE, self.find_max_vert(result)]



    def get_monthly_stats(self, currdate, prov_filter):

        '''
        Finds the amount of documents for each of the following weeks for zxxk,
        dearedu, ziyuanku, twentyOne across 3 months

        '''

        on_date = currdate
        currdate = datetime.strptime(currdate + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
        s_date = currdate - timedelta(days=3*31 - currdate.weekday())
        s_date = s_date + timedelta(days=7-s_date.weekday())                             #then find the next nearest monday in the future
        START_FROM = s_date.strftime('%Y-%m-%d') + ' 00:00:00'
        time_expressions, string_list = [], []

        while True:
            start = s_date.strftime('%Y-%m-%d') + ' 00:00:00'
            s_date += timedelta(days=7)
            end = s_date.strftime('%Y-%m-%d') + ' 00:00:00'
            condition = {"$sum": {"$cond": [{"$and": [{"$gte": ["$res_date", start]},{"$lt": ["$res_date", end]}]}, 1, 0]}}
            if s_date > currdate:
                break
            time_expressions.append(condition)
            sbtl = start[6:-9].split('-')
            ebtl = end[6:-9].split('-')
            string_list.append('{}月 {}日-{}月 {}日'.format(sbtl[0], sbtl[1], ebtl[0], ebtl[1]))
            END_TO = end

        match_date_cond = {"res_date": {"$gte": START_FROM, "$lt": END_TO}}
        match_site_cond = {"$or": [{'site_id': 'zxxk'},{'site_id': 'dearedu'},{'site_id': 'twentyOne'},{'site_id': 'ziyuanku'}]}
        match_list = [match_site_cond, match_site_cond]
        if int(prov_filter) != 0:
            match_list.append({'res_province': self.provdict[int(prov_filter)]})
        matcher = {"$match": {"$and": match_list}}

        #groupconstruction
        grouper = {"$group": {}}
        grouper["$group"]["_id"] = {"site": "$site_id"}
        counter = 1
        for conditions in time_expressions:
            grouper["$group"][str(counter)] = conditions
            counter += 1

        PIPELINE = [matcher, grouper]
        aggregate_result = list(self.collection.aggregate(PIPELINE))

        doc_counter = 0
        index = 0
        result = []
        for data in aggregate_result:
            result.append([self.site_translations[data["_id"]["site"]]])
            for i in range(1, len(string_list)+1):
                doc_num = data[str(i)]
                doc_counter += doc_num
                result[index].append(doc_num)
            result[index].append(doc_counter)
            doc_counter = 0
            index += 1

        sdl = START_FROM[:-9].split('-')
        edl = END_TO[:-9].split('-')
        TITLE =  u'{}年{}月{}日-{}年{}月{}日 近三月资料数量增长情况 ({})'.format(sdl[0],sdl[1],sdl[2],edl[0],edl[1],edl[2], self.provdict[int(prov_filter)])
        result = sorted(result, key=lambda x: x[-1], reverse=True)
        return [on_date ,TITLE, string_list + ['Total'], self.find_max_vert(result)]


    def find_max_vert(self, result):

        '''
        finds the biggest value in a given column
        '''

        max_row, max_col = len(result), len(result[0])
        for i in range(1, max_col-1):
            MAX_VERT = 0
            r, c = 0, 0
            for j in range(0, max_row):
                if result[j][i] > MAX_VERT:
                    MAX_VERT = result[j][i]
                    r, c = j, i
            if MAX_VERT != 0:
                result[r][c] = [result[r][c]]
        return result



if __name__ == '__main__':
    stats = spider_stats()
    #
    s = datetime.today()
    #stats.get_subject_stats('2017-08-14', 0)
    stats.update_stat_col()
    print datetime.today() -s
