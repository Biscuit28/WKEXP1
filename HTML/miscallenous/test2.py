

from collections import defaultdict
import time

point_dict = {1: 284, 2:600, 3:1134, 4:1438, 5: 5070, 6: 2028, 7: 491, 8: 323, 9:161, 10:249}
#sorted_point_dict = sorted(point_dict, key = lambda k: len(point_dict[k]), reverse=True)


#this is a simulation

wasted_points = 0
incomplete_users = 0


def choose_download(usrpoints):

    sorted_points = sorted(point_dict, key = lambda k: point_dict[k], reverse=True)
    for i in sorted_points:
        if i <= usrpoints and point_dict[i] > 0:
            print i
            point_dict[i] -= 1
            return usrpoints - i
    global wasted_points, incomplete_users
    if usrpoints != 10:
        print 'wasted', usrpoints
        incomplete_users = incomplete_users + 1
        wasted_points = wasted_points + usrpoints
    return 0

def choose_download_2(usrpoints):


    points = usrpoints

    while points > 0:
        #print '--', points
        if point_dict[points] > 0:
            print points
            point_dict[points] -= 1
            return usrpoints - points
        points -= 1
    global wasted_points, incomplete_users
    if usrpoints != 10:
        print 'wasted', usrpoints
        incomplete_users = incomplete_users + 1
        wasted_points = wasted_points + usrpoints
    return 0


def choose_download_3(usrpoints):
    #step 1, find all possible factors from 10 to 1
    pass


def get_all_possible_sums_of_(num):
    '''
    Finds all the possible sums from 1-num
    '''

    sum_dict = defaultdict(list)

    def check_for_branch(n, j, start=[]):
        result = []
        if j not in sum_dict:
            result.append(start)
            return result
        else:
            for leaves in sum_dict[j]:
                sums = start + leaves #list, list
                sums.sort()
                if sums not in sum_dict[n]:
                    result.append(sums)
        result.sort()
        return result

    for n in range(1, num + 1):
        for i in range(1, num + 1):
            j = n - i
            if n not in sum_dict:
                sum_dict[n] = check_for_branch(n, j, start=[i])
            else:
                sum_dict[n] += check_for_branch(n, j, start=[i])
            if j == 0:
                break
    return sum_dict


sum_search = get_all_possible_sums_of_(25)
print sum_search[10]





# global_counter = 0
#
# for i in range(0,5909):
#     global_counter += 1
#     print '-----download----'
#     new_user = 10
#     breaker = False
#     while new_user != 0:
#         new_user = choose_download_2(new_user)
#
#     print point_dict
# print global_counter
# print wasted_points
#print incomplete_users
