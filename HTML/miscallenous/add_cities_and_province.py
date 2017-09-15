# -*- coding: utf-8 -*-
import pymongo

host='10.1.1.13'
port = 27017
client = pymongo.MongoClient(host, port)

def add_cities_and_provinces():

    CITIES = [u'阿坝',u'阿拉善',u'安顺',u'鞍山',u'巴彦淖尔',u'巴中',u'白银',u'百色',
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
    u'自贡',u'遵义']

    PROVINCES = [u'北京',u'天津',u'上海',u'重庆',u'河北',u'辽宁',u'黑龙江',u'吉林',u'山东',u'山西',u'安徽',
    u'浙江',u'江苏',u'江西',u'广东',u'福建',u'海南',u'河南',u'湖北',u'湖南',u'四川',u'云南',u'贵州',
    u'陕西',u'甘肃',u'青海',u'宁夏',u'内蒙古',u'广西',u'西藏', u'新疆', u'香港',u'澳门', u'台湾']

    city_collection = client.config.city
    province_collection = client.config.province

    for c in CITIES:
        if city_collection.find_one({'name' : c}) == None:
            city_collection.insert_one({'name' : c})
            print c

    for p in PROVINCES:
        if province_collection.find_one({'name' : p}) == None:
            province_collection.insert_one({'name' : p})
            print p

def add_misc():

    collection = client.dict.userdict

    with open('misc.txt') as f:
        for line in f:
            line = line.split()

            doc = {"word": line[0], "tag": line[1]}
            if collection.find_one(doc) == None:
                collection.insert_one(doc)
                print line

def add_misc_2():

    collection = client.config.sites

    data = []

    data.append({'id': 'ks5u', 'type': 'xkw_ks5u', 'name': u'高考资源网'})
    data.append({'id': 'zk5u', 'type': 'xkw_zk5u', 'name': u'中考资源网'})
    data.append({'id': 'twentyOne', 'type': 'xkw_twentyOne', 'name': u'21世纪'})
    data.append({'id': 'ht88', 'type': 'xkw_ht88', 'name': u'育星教育网'})
    data.append({'id': 'daliankao', 'type': 'xkw_daliankao', 'name': u'全国大联考'})
    data.append({'id': 'jtyhjyGaozhong', 'type': 'xkw_jtyhjyGaozhong', 'name': u'金太阳好教育'})
    data.append({'id': 'canpoint', 'type': 'xkw_canpoint', 'name': u'全品教学网'})
    data.append({'id': 'ziyuanku', 'type': 'xkw_ziyuanku', 'name': u'中华资源库'})
    data.append({'id': 'xueyou', 'type': 'xkw_xueyou', 'name': u'学优网'})
    data.append({'id': 'hengqian', 'type': 'xkw_hengqian', 'name': u'恒谦教育网'})
    data.append({'id': 'jb1000', 'type': 'xkw_jb1000', 'name': u'教育资源网'})
    data.append({'id': 'xiangpi', 'type': 'xkw_xiangpi', 'name': u'橡皮网'})
    data.append({'id': 'dearedu', 'type': 'xkw_dearedu', 'name': u'第二教育网'})
    data.append({'id': 'tl100', 'type': 'xkw_tl100', 'name': u'天利网'})

    for doc in data:
        if collection.find_one(doc) == None:
            collection.insert_one(doc)
            print doc

def add_dearedu_data():

    vcollection = client.config.version
    scollection = client.config.subject

    subject_set = set([u'语文', u'数学', u'英语', u'物理', u'化学', u'生物', u'政治', u'地理', u'历史'])

    G_VERSION = [u'新人教',u'苏教版',u'粤教版',u'语文版',u'北京版',u'北师大',u'鲁人版',u'新人教A版',
    u'新人教B版',u'北师大版',u'湘教版',u'新人教版',u'译林牛津版',u'外研版',u'冀教版',u'人教实验版',
    u'重庆大学版',u'浙科版',u'浙教版',u'中图版',u'沪教版',u'鲁教版',u'鲁科版',u'岳麓版',u'人民版',
    u'大象版',u'苏科版',u'人教实验版(B)',u'沪科版',u'江苏版',u'教科版']

    C_VERSION = set([u'新人教',u'语文版',u'苏教版',u'北师大',u'鲁教版',u'鄂教版',u'（新）新人教',u'苏科版',
    u'（新）浙教版',u'（新）新目标',u'外研版',u'（新）仁爱版',u'冀教版',u'仁爱版',u'（新）沪科版',u'教科版',
    u'新人教版',u'（新）鲁教版',u'沪教版',u'鲁教版五四制',u'粤教版',u'川教版',u'岳麓版',u'华师大',u'旧人教版',
    u'中华书局',u'陕教版',u'人民版',u'湘教版',u'湘师版',u'人教版五四制',u'（新）粤教版',u'人教实验版',u'上教版',
    u'北京版',u'苏教版旧人教版',u'(新)苏科版',u'(新)北师大版',u'(新)教科版',u'沪科版',u'粤教沪科版',u'牛津深圳版',
    u'牛津沈阳版',u'牛津广州版',u'上海牛津版',u'(新)牛津版',u'(新)外研版',u'(新)冀教版',u'人教新目标',u'牛津译林版',
    u'浙教版',u'青岛版',u'(新)华东师大版',u'(新)沪科版',u'(新)湘教版',u'华东师大版',u'长春版',u'人教实验',u'(新)新人教版',
    u'(新)苏教版',u'(新)语文版',u'河大版',u'（新）苏科版',u'（新）北师大',u'北师大版',u'（新）外研版',u'（新）牛津版',
    u'(新)新人教',u'济南版',u'鲁科版',u'(新)济南版',u'（新）星球版',u'中图版',u'商务星球版',u'（新）语文版',u'上海五四制',
    u'（新）湘教版'])

    X_VERSION = set([u'上册',u'新人教版',u'北师大版',u'苏教版',u'西师大版',u'冀教版',u'沪教版',u'青岛版',u'下册',
    u'青岛版五四制',u'青岛版六三制',u'苏教牛津版',u'牛津深圳版',u'北师大版(一起)',u'人教(新起点)',
    u'广州版',u'冀教版(一起)',u'外研版(一起)',u'新路径(一起)',u'北京版',u'外研版',u'人教pep',
    u'人教(新版)',u'北师大版(三起)',u'冀教版(三起)',u'外研版(三起)',u'闽教版(三起)',u'湘少版',
    u'重大版',u'人教精通版(三起)',u'新路径(三起)',u'浙教版',u'语文S版',u'语文A版',u'长春版',
    u'湘教版',u'教科版',u'鲁教版',u'鄂教版'])

    g_v = ''
    for q in G_VERSION:
        g_v += q + ' '

    g_v.strip()

    c_v = ''
    for w in C_VERSION:
        c_v += w + ' '
    c_v.strip()

    x_v = ''
    for e in X_VERSION:
        x_v += e + ' '
    x_v.strip()

    vcollection.insert_one({"dearedu": {"elementary":x_v, "juniorhigh": c_v, "highschool": g_v}})

    for a in subject_set:
        if scollection.find_one({"name": a}):
            continue
        else:
            scollection.insert_one({"name": a})

def add_ip():

    collection = client.config.setup
    collection.insert_one({"host": host, "port": port})


def add_ht88_subject():

    collection = client.config.subject

    subject_dict = {'语文':'http://www.ht88.com', '数学': 'http://shuxue.ht88.com', '英语': 'http://yingyu.ht88.com',
                    '物理': 'http://wuli.ht88.com', '化学': 'http://huaxue.ht88.com', '生物': 'http://shengwu.ht88.com',
                    '历史': 'http://lishi.ht88.com', '地理': 'http://dili.ht88.com', '政治': 'http://zhengzhi.ht88.com'}
    C=0
    for k in subject_dict.keys():
        if collection.find_one({'name': k}) == None:
            C+=1
            collection.insert_one({'name': k})
    print C


add_ht88_subject()
