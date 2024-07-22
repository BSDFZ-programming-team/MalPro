import os
import csv
csv_file = 'trainLabels_all.csv'

data = {}
with open(csv_file, mode='r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        key = row[0]
        value = row[1]
        data[key] = value
with open('TrainLabels.csv', 'w') as f:
    f.write('"Id","Class"\n')
    for ams in os.listdir('./train'):
        out = ams.split('.asm')[0]
        f.write('"'+out+'"'+","+data[out]+'\n')



