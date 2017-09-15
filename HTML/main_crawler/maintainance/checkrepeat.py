import pymongo, sys, pprint
sys.path.insert(0, '/opt/git/Spider/src/')
from data import conf


class repeater:

    '''
    Removes any repeating documents from some specified collection.
    A repeating document is defined as a document whos url is not unique
    '''

    def __init__(self):

        self.client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        self.main_collection = self.client.spider.res
        self.collection_names = self.client.spider.collection_names(include_system_collections=False)
        self.collection_names.remove('res')
        self.collection_names.remove('similar')
        self.collection_names.remove('xkw')


    def start(self):

        while True:
            pprint.pprint(self.collection_names)
            userin = raw_input('please choose a site to check or press (Q) to quit: ')
            if userin in self.collection_names:
                self.check(userin)
            if userin.lower() == 'q':
                break


    def check(self, site):

        def find_repeats(res=False):
            if not res:
                print 'from', site
                site_collection = self.client.spider.get_collection(site)
            else:
                print 'from res'
                site_collection = self.main_collection
            site_documents = site_collection.find({"site_id": site})
            SITECOUNT = site_documents.count()
            print 'original count --> ', SITECOUNT
            print 'distinct urls --> ', len(site_documents.distinct('res_url'))
            url_set = set()
            repeating_urls_set = set()
            for document in site_documents:
                document_id = document['_id']
                document_url = document['res_url']
                if document_url in url_set:
                    repeating_urls_set.add(document_url)
                else:
                    url_set.add(document_url)
            pprint.pprint(repeating_urls_set)
            while True:
                userin = raw_input('{} urls have repating documents. Remove duplicates from collection? (Y/N)): '.format(len(repeating_urls_set)))
                if userin.lower() == 'y':
                    self.remove(repeating_urls_set, site_collection)
                    break
                elif userin.lower() == 'n':
                    break
        find_repeats()
        find_repeats(res=True)


    def remove(self, url_set, collection):

        query_score = {'res_date': 1, 'res_url': 1, 'res_title': 1, 'site_id': 1,
                    'res_city': 1, 'res_county': 1, 'res_province': 1, 'res_class': 1,
                    'res_downcount': 1, 'res_point': 1, 'res_type': 1, 'res_file': 5,
                    'res_intro': 1, 'res_id': 1, 'res_subject': 1, 'res_version': 1}
        LOSER_LIST = []
        repeat_count = len(url_set)
        counter = 0
        for url in url_set:
            HIGHSCORE_POINTS = 0
            HIGHSCORE_USERNAME = ''
            for document in collection.find({'res_url': url}):
                doc_name = document['_id']
                SCORE = 0
                for query in query_score.keys():
                    try:
                        qresult = document[query]
                    except Exception, e:
                        continue
                    if qresult == None or qresult == '':
                        continue
                    else:
                        SCORE += query_score[query]
                if SCORE > HIGHSCORE_POINTS:
                    HIGHSCORE_POINTS = SCORE
                    LOSER_LIST.append(HIGHSCORE_USERNAME)
                    HIGHSCORE_USERNAME = doc_name
                else:
                    LOSER_LIST.append(doc_name)
            counter += 1
            print 'WINNER: ', HIGHSCORE_USERNAME, url, HIGHSCORE_POINTS, '{}/{}'.format(counter, repeat_count)
        collection.delete_many({'_id':{'$in': LOSER_LIST}})
        print len(LOSER_LIST), 'removed'






if __name__ == '__main__':
    repeater = repeater()
    repeater.start()
