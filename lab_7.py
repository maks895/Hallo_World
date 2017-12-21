import csv
import op

file_name_r = "user.csv"
file_name_w = "user_.csv"

obj = op.Main()

obj.fromFile(file_name_r)

obj.sortBy('st')

obj.intoFile(file_name_w)
