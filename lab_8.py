import csv

class Main():

    reader = None
    header = None

    data = []

    def __init__(self):
        pass

    def fromFile(self, file_n):
        try:
            with open(file_n, 'r') as file:
                self.reader = csv.DictReader(file)
                #self.header = next(self.reader)

                for row in self.reader:
                    self.data.append(row)
        except:
            return -1

    def intoFile(self, file_n):
        try:
            with open(file_n, 'w') as file:
                fieldnames = ['name_of_faculty','count_of_student','midle_point','count_of_excellence','count_of_loser']
                csv_writer = csv.DictWriter(file, fieldnames = fieldnames, delimiter = '\t')

                csv_writer.writeheader()
                csv_writer.writerows(self.data)
        except:
            return -1

    def sortBy(self, param):
        flag = True

        while flag == True:
            flag = False

            for id in range(len(self.data) - 1):
                if param == 'str':
                    if self.compareRows(self.data[id], self.data[id + 1]) == 1:
                        continue
                else:
                    numb_1 = int(self.data[id]['count_of_excellence'])
                    numb_2 = int(self.data[id + 1]['count_of_excellence'])

                    if numb_1 < numb_2:
                        continue

                row = self.data[id]
                self.data[id] = self.data[id + 1]
                self.data[id + 1] = row
                flag = True


    def compareRows(self, str_1, str_2):
        str_11 = str_1['name_of_faculty'].lower()
        str_22 = str_2['name_of_faculty'].lower()

        for id in range(len(str_1)):
            if str_11[id] == str_22[id]:
                continue
            elif str_11[id] < str_22[id]:
                return 1
            else:
                return 2