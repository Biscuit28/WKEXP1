

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

    for i in range(0, 6-len(num_arr)):
        FORMAT.pop()

    if len(num_arr) == 2:
        FORMAT = ['M', 'D']

    # if len(num_arr) == 6:
    #     FORMAT = ['Y','M', 'D', 'H', 'Min', 'S'] #most probably
    # if len(num_arr) == 5:
    #     FORMAT = ['Y', 'M', 'D', 'H', 'Min'] #most proably
    # if len(num_arr) == 4:
    #     FORMAT = ['Y', 'M', 'D', 'H']

    if len(num_arr) == 2:
        if len(num_arr[0]) == 1:
            num_arr[0] += 0 + num_arr[0]
        if len(num_arr[1]) == 1:
            num_arr[1] += 0 + num_arr[1]
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
