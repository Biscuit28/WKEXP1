import pymongo
def find():

    site = ''
    client = None


    userin = raw_input('Enter port (10.1.1.13, localhost): ')

    client = pymongo.MongoClient(userin, 27017)

    while True:

        type_string = ''
        subject_string = ''
        version_string = ''

        while True:

            userin = raw_input('Enter collection: ')

            site = userin.lower()

            if userin == 'canpoint':
                collection = client.spider.canpoint
                break
            elif userin == 'daliankao':
                collection = client.spider.daliankao
                break
            elif userin == 'dearedu':                                            #DONE
                collection = client.spider.dearedu
                break
            elif userin == 'hengqian':                                              #DONE
                collection = client.spider.hengqian
                break
            elif userin == 'ht88':                                              #DONE
                collection = client.spider.ht88
                break
            elif userin == 'jb1000':                                                        #DONE
                collection = client.spider.jb1000
                break
            elif userin == 'jtyhjyGaozhong':                                                  #DONE
                collection = client.spider.jtyhjyGaozhong
                break
            elif userin == 'tl100':                           #DONE
                collection = client.spider.tl100
                break
            elif userin == 'twentyOne':                                                  #DONE
                collection = client.spider.twentyOne
                break
            elif userin == 'xiangpi':
                collection = client.spider.xiangpi
                break                                              #DONE
            elif userin == 'xueyou':
                collection = client.spider.xueyou
                break                                               #DONE
            elif userin == 'ziyuanku':
                collection = client.spider.ziyuanku
                break                                              #DONE *
            elif userin == 'zk5u':
                collection = client.spider.zk5u
                break                                                    #DONE
            elif userin == 'ks750':
                collection = client.spider.ks750
                break                                                  #DONE
            elif userin == 'ks5u':
                collection = client.spider.ks5u
                break
            else:
                print 'bad input'

        type_set = set()
        version_set = set()
        subject_set = set()

        fcount = collection.count()
        icount = 0
        for d in collection.find():
            try:
                if 'res_type' in d:
                    res_type = d['res_type']
                    type_set.add(res_type)

                if 'res_version' in d:
                    res_version = d['res_version']
                    version_set.add(res_version)
                if 'res_subject' in d:
                    res_subject = d['res_subject']
                    subject_set.add(res_subject)

            except Exception, e:
                print 'error', e

            icount += 1

            print (float(icount)/float(fcount))*100, '%'


        print '===========type set=============='
        for i in type_set:
            print i
            try:
                type_string += i + ' '
            except:
                continue
        type_string = type_string.strip()
        print '==========version_set============'
        for j in version_set:
            print j
            try:
                version_string += j + ' '
            except:
                continue
        version_string = version_string.strip()
        print '==========subject set============'
        for k in subject_set:
            print k
            try:
                subject_string +=  k + ' '
            except:
                continue
        subject_string = subject_string.strip()

        while True:
            userin = raw_input('Do you want to add to database? (Y/N): ')
            userin.lower()

            if userin == 'y':

                collection = client.config.sitetypes

                if collection.find_one({'site': site}) == None:
                    document = {'site': site, 'res_types': type_string, 'res_versions': version_string, 'res_subjects': subject_string}
                    collection.insert_one(document)
                else:
                    d = collection.find_one({'site': site})
                    _id = d['_id']
                    d['res_types'] = type_string
                    d['res_versions'] = version_string
                    d['res_subjects'] = subject_string

                    collection.update_one({'_id': _id}, {"$set": d}, upsert=False)

                break

            elif userin == 'n':
                break
            else:
                print 'bad input'




find()
