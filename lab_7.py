import csv
import op

file_name_r = "user.csv"
file_name_w = "user_.csv"

obj = op.Main()

obj.fromFile(file_name_r)

obj.sortBy('st')

obj.intoFile(file_name_w)


f = open('input.txt')
N = f.readline()
d = {}
for line in f:
    words = line.strip().split(' - ')
    en = words[0]
    lat = words[1].split(', ')
    for key in lat:
        if key in d:
            d[key].append(en)
        else:
            d[key] = [en]
f.close()

for key in d:
    d[key].sort()


g = open('output.txt', 'w')
g.write(str(len(d)) + '\n')
for lat in sorted(d):
    g.write(lat + ' - ' + ', '.join(d[lat]) + '\n')

g.close()