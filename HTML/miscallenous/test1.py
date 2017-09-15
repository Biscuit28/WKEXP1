import pymongo, urllib2
from pyquery import PyQuery as pq

def format_date(date):

    FORMAT = ['Y','M', 'D', 'H', 'Min', 'S']
    num_arr, digit = [], ''
    Listen_state = False
    for ele in date:
        if ele.isdigit():
            Listen_state = True
        elif not ele.isdigit() and Listen_state:
            num_arr.append(digit)
            digit = ''
            Listen_state = False
        if Listen_state:
            digit += ele
    if digit != '':
        num_arr.append(digit)
    new_date_string = ''
    if len(num_arr) == 2:
        return '2017-{}-{} 00:00:00'.format(num_arr[0], num_arr[1])
    for j in range(len(FORMAT)):
        F = FORMAT[j]
        try:
            N = num_arr[j]
        except:
            N = '00'
        if len(N) == 1:
            N = '0' + N
        if F == 'Y':
            if len(N) < 3:
                N = str(2000 + int(N))
            new_date_string += N +'-'
        if F == 'M':
            new_date_string += N +'-'
        if F == 'D':
            new_date_string += N +' '
        if F == 'H' or F == 'Min':
            new_date_string += N+':'
        if F == 'S':
            new_date_string += N
    return new_date_string


client = pymongo.MongoClient('10.1.1.13', 27017)

coll = client.spider.res

for k in coll.find({"res_date": ''}):
    url= k['res_url']
    _id = k['_id']
    html = unicode(urllib2.urlopen(url).read(), 'gb18030')
    d = pq(html)
    date = format_date(d('#lblUpdateTime').text())
    print date
    coll.update({'_id': _id}, {'res_date': date}, multi=False, upsert=False)
