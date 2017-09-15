# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo,logging, re, platform, sys, time, tools
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


import signal

def canpoint(count=5):

    client = pymongo.MongoClient('10.1.1.13', 27017)
    collection = client.robots.canpoint

    driver=webdriver.PhantomJS()

    if collection.count() == 0:
        r_index = 0
    else:
        youngest_robot = collection.find({}).sort('r_index', -1).limit(1)[0]
        r_index = youngest_robot['r_index']

    txt_loginpassword, txt_loginpassword1 = '111111', '111111'
    txt_pwquestion, txt_pwanswer = 'what is your name?', 'toseektheholygrail!'
    txt_workplace, txt_realname, txt_birthday = 'sweatshopfactory', 'Tom Doretto', '1989-11-09'
    txt_telephone, txt_mobile, txt_qq = '18600145389', '18600145389', '231313123123'
    txt_address, txt_zip	= '860HP Dragstrip Lane', '123456'
    txt_job = 'bank robbing'

    def fill_in(driver):

        print 'creating {} ...'.format(txt_loginname)

        driver.get('http://www.canpoint.cn/Register.aspx')

        driver.find_element_by_id('txt_loginname').send_keys(txt_loginname)
        driver.find_element_by_id('txt_realname').send_keys(txt_realname)
        driver.find_element_by_id('txt_loginpassword').send_keys(txt_loginpassword)
        driver.find_element_by_id('txt_loginpassword1').send_keys(txt_loginpassword1)
        driver.find_element_by_id('txt_pwquestion').send_keys(txt_pwquestion)
        driver.find_element_by_id('txt_pwanswer').send_keys(txt_pwanswer)
        driver.find_element_by_id('txt_mail').send_keys(txt_mail)

        driver.find_element_by_xpath("//select[@id='ddl_szsf_province']").click()
        driver.find_element_by_xpath("//select[@id='ddl_szsf_province']/option[@value='1']").click()
        tools.wait_for_load(driver)

        driver.find_element_by_xpath("//select[@id='txtuserjob']/option[@value='教师']").click()
        driver.find_element_by_xpath("//select[@id='txtschoolType']/option[@value='小学']").click()

        driver.find_element_by_id('txt_workplace').send_keys(txt_workplace)
        driver.find_element_by_id('txt_mobile').send_keys(txt_mobile)
        driver.find_element_by_id('txt_birthday').send_keys(txt_birthday)
        driver.find_element_by_id('txt_telephone').send_keys(txt_telephone)
        driver.find_element_by_id('txt_qq').send_keys(txt_qq)
        driver.find_element_by_id('txt_address').send_keys(txt_address)
        driver.find_element_by_id('txt_zip').send_keys(txt_zip)
        driver.find_element_by_id('txt_job').send_keys(txt_job)

        driver.find_element_by_xpath("//input[@type='checkbox']").click()
        driver.find_element_by_id('btn_save').click()

        print 'Hi ' + txt_loginname +'!'

    while count > 0:
        r_index += 1
        txt_loginname = 'xfrbd_' + str(r_index)
        txt_mail = txt_loginname + '@123.com'

        try:
            fill_in(driver)
        except Exception, e:
            print 'Birthing complications... ', e
            driver.close()
            driver.quit()
            quit()

        r_birthday = datetime.today().strftime('%Y/%m/%d %H:%M:%S')

        doc = {
        'r_name': txt_loginname,
        'r_index': r_index,
        'r_hp': 10,
        'r_birthday': r_birthday,
        'r_pw': '111111'
        }

        collection.insert_one(doc)
        count -= 1

    print 'done'
    driver.close()
    driver.quit()

# client = pymongo.MongoClient('10.1.1.13', 27017)
# collection = client.spider.canpoint
#
# for doc in collection.find():
#     _id = doc['_id']
#     collection.update({'_id': _id}, {"$set": {'res_point': int(doc['res_point'])}}, upsert=False)

#canpoint(count=50)
