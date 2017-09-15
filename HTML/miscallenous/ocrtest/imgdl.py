import urllib2

#http://www.canpoint.cn/GetImage.aspx?id=601121

def get_image():

    advanced = raw_input('canpoint? (Y/N): ')

    advanced.lower()

    if advanced == 'y':

        main = 'http://www.canpoint.cn/'
        target = raw_input('enter img dl from canpoint: ')

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        opener.addheaders = [('User-agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')]

        urllib2.install_opener(opener)

        req = urllib2.Request(main)
        urllib2.urlopen(req)

        print cj

        FILE = urllib2.urlopen(url)
        IMAGE = FILE.read()
        #5605
        open('out.jpg', 'wb').write(IMAGE)


    if advanced == 'n'
        url = raw_input('enter img src: ')

        FILE = urllib2.urlopen(url)
        IMAGE = FILE.read()
        #5605
        open('out.jpg', 'wb').write(IMAGE)

        print 'success'

get_image()
