import pymongo, sys, traceback
from multiprocessing import Process

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf

class rm_none:

    '''
    adds chosens fields (whose value is set by default to '') to either all or a
    individual collections in spider database. If fixall is set to true,
    it will automatically apply changes to all collections. If rm is true, it will
    remove the chosen fields from either chosen or all collections
    '''

    def __init__(self, fixall=True, rm=False):

        self.fixall = fixall
        self.rm = rm
        while True:
            userin = raw_input('Fix all? (Y/N): ')
            userin.lower()
            if userin == 'y':
                self.fixall = True
            elif userin == 'n':
                self.fixall = False
            else:
                print 'try again'
                continue
            print '*note if adding, each field will have by default EMPTY ("") value'
            userin = raw_input('remove field or add field (R/A)?: ')
            userin.lower()
            if userin == 'r':
                self.rm = True
                break
            elif userin == 'a':
                self.rm = False
                break
            else:
                print 'try again'
                continue
        while True:
            userin = raw_input('Enter the space seperated target fields: ')
            self.keys = userin.split()
            print self.keys
            confirm = raw_input('are you sure the above is correct? (Y/N): ')
            if confirm.lower() == 'y':
                break
            else:
                self.keys = []


    def find_none(self, coll_name):

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collection = client.spider.get_collection(coll_name)

        try:
            print 'fixing values for ', coll_name
            for document_keys in self.keys:
                if not self.fixall:
                    print document_keys
                value = ''
                if document_keys == 'site_id':
                    value = coll_name
                if not self.rm:
                    collection.update({document_keys: {'$exists': False}}, {"$set": {document_keys: value}}, upsert=False, multi=True)
                else:
                    collection.update({}, {'$unset': {document_keys: '1'}}, multi=True)
            print 'fixed', coll_name
            client.close()
        except Exception:
            traceback.print_exc()
            print coll_name, 'could not be added'
            client.close()


    def start(self):

        client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
        collections = client.spider.collection_names()
        collections.remove(u'system.indexes')
        collections.remove(u'similar')
        collections.remove(u'xkw')
        client.close()

        if self.fixall:
            processes = []
            for task in collections:
                p = Process(target = self.find_none, args = (task,))
                p.start()
                processes.append(p)
            for j in processes:
                j.join()
        else:
            while True:
                userin = raw_input('Enter name of collection you want to fix or enter Q to quit: ')
                if userin in collections:
                    self.find_none(userin)





if __name__ == "__main__":
    rmnone = rm_none(fixall=True, rm=True)
    rmnone.start()
