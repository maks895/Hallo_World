import random
random.shuffle(koloda)
koloda = [6,7,8,9,10,2,3,4,11] * 4

print('�������� � ����?')
count = 0

while True:
    choice = input('������ ����� �����? y/n\n')
    if choice == 'y':
        current = koloda.pop()
        print('��� �������� ����� ������������ %d' %current)
        count += current
        if count > 21:
            print('��������, �� �� ���������')
            break
        elif count == 21:
            print('����������, �� ������� 21!')
            break
        else:
            print('� ��� %d �����.' %count)
    elif choice == 'n':
        print('� ��� %d ����� � �� ��������� ����.' %count)
        break

def parse(code):
    new = ''
    for c in code:
        if c in '><+-.,[]':
            new += c
    return new
def parse(code):
    return ''.join(c for c in code if c in '><+-.,[]')