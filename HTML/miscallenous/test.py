def check_date(sdate, edate):

    sdate = sdate.split('-')
    edate = edate.split('-')
    def check(index=0):
        MAX_COUNTER = 2
        if int(sdate[index]) > int(edate[index]):
            return False
        elif int(sdate[index]) == int(edate[index]):
            if index == MAX_COUNTER:
                return False
            return check(index=index+1)
        else:
            return True
    return check()


while True:
    sdate = raw_input('start Date: ')
    edate = raw_input('end Date: ')
    print 'is date valid? ', check_date(sdate, edate)
