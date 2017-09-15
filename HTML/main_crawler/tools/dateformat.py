def compare_date(sdate, edate):

    '''
    recursively checks if sdate is bigger than edate

    Expects date format to be  YY-mm-dd
    '''
    print sdate
    sdate = sdate.split('-')
    edate = edate.split('-')
    def check(index=0):
        if int(sdate[index]) > int(edate[index]):
            return False
        elif int(sdate[index]) == int(edate[index]):
            if index == 2:
                return False
            return check(index=index+1)
        else:
            return True
    return check()


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
