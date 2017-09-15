import time, cookielib

def wait_for_load(driver):

    while True:
        first = driver.find_element_by_xpath('/html').get_attribute('innerHTML')
        time.sleep(0.5)
        second = driver.find_element_by_xpath('/html').get_attribute('innerHTML')
        if first == second:
            print 'loaded'
            break
        else:
            print 'loading'
            pass


def get_extension(file, ext=''):

    for c in reversed(file):
        if c == '.':
            break
        ext = c + ext
    return ext


def canpoint_users():
    return ({'largest'},{'xkw001': 10, 'xkw002': 10, 'xkw003': 7, 'xkw004': 10, 'xkw005':10})


def to_cookielib_cookie(selenium_cookie):

    importantlist = ['name', 'value', 'domain', 'path', 'secure', 'expiry']

    for k in importantlist:
        if k not in selenium_cookie:
            selenium_cookie[k] = None

    return cookielib.Cookie(
        version=0,
        name=selenium_cookie['name'],
        value=selenium_cookie['value'],
        port='80',
        port_specified=False,
        domain=selenium_cookie['domain'],
        domain_specified=True,
        domain_initial_dot=False,
        path=selenium_cookie['path'],
        path_specified=True,
        secure=selenium_cookie['secure'],
        expires=selenium_cookie['expiry'],
        discard=False,
        comment=None,
        comment_url=None,
        rest=None,
        rfc2109=False
    )


def put_cookies_in_jar(selenium_cookies, cookie_jar):
    for cookie in selenium_cookies:
        print cookie
        cookie_jar.set_cookie(to_cookielib_cookie(cookie))
