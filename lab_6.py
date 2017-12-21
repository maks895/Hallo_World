

R_0 = R_1 = R_2_1 = R_2_2 = -2000


N = int(input())



for i in range(N):
    num = int(input())
    if num % 3 == 0:
        R_0 = max(R_0, num)

    elif num % 3 == 1:
        R_1 = max(R_1, num)
    elif num % 3 == 2:

        if num > R_2_1:
            R_2_1, R_2_2 = num, R_2_1

        elif num > R_2_2:
            R_2_2 = num

R = max(R_0 + R_1, R_2_1 + R_2_2)

if R < 0:


    R = 1
print("Вычисленное контрольное значение: {}".format(R))


result = int(input())
if R == result:
    print("Контроль пройден")
else:
    print("Контроль не пройден")