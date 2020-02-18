import csv,os
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
with open('musicitems.csv','rt',encoding='utf-8') as csv_file:
  with open('composers1.csv','wt',encoding='utf-8') as out_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line = 100
    for row in csv_reader:
            print(f'{line},{row[1]},{row[0]},{row[2]}-01-01,{row[3]}-01-01',file=out_file)
            line = line + 1