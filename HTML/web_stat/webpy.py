import web, pymongo, traceback, sys, crawlstats, datetime, pprint
sys.path.insert(0, '/opt/git/Spider/src/')
from data import conf

render = web.template.render('templates/',  globals={"type": type}) #if you want to use some python funcitonalities pass them to globals in web.template.render

urls = ('/',    'index',
        '/subjectstats', 'subject_stats',
        '/monthlystats', 'monthly_stats',)

client = pymongo.MongoClient(conf.mongo.ip, conf.mongo.port)
stat = crawlstats.spider_stats()

class index:

    def GET(self):
        return render.index()

class subject_stats:

    def GET(self):
        weekday = datetime.datetime.today().weekday()
        default_date = datetime.datetime.today() - datetime.timedelta(days=7+weekday)
        default_date = default_date.strftime('%Y-%m-%d')
        i = web.input(sdate=default_date, province_filter="0")
        findings = stat.get_subject_stats(i.sdate, i.province_filter)
        return render.subject_stats(findings)

class monthly_stats:

    def GET(self):
        default_date = datetime.datetime.today()
        default_date = default_date.strftime('%Y-%m-%d')
        i = web.input(currdate=default_date, province_filter="0")
        findings = stat.get_monthly_stats(i.currdate, i.province_filter)
        return render.monthly_stats(findings)



if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
