import math

FOV = 180.0
CONST =  20
UNIT_D = 1
num_dict = {}

deg = 0

for i in range(1,11):
    print deg
    num_dict[i-1] = math.radians(deg)
    deg += CONST

print num_dict

a = '12349'
b = '32194'

def calculate_similarity(a,b):

    MAX_DISTANCE = len(a) + len(b)

    def calculate_position(s):

        position_x = 0
        position_y = 0

        for c in s:
             rad = num_dict[int(c)]
             x_translate = math.cos(rad)
             y_translate = math.sin(rad)

             position_x += x_translate
             position_y += y_translate

        return (position_x, position_y)

    r1 = calculate_position(a)
    r2 = calculate_position(b)
    distance = math.hypot(r1[0]-r2[0], r1[1]-r2[1])

    return 100 - (distance/MAX_DISTANCE)*100

print calculate_similarity(a,b)
