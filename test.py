# from numpy import average

# file = open("brew_data.csv", "r")
# data = file.read().splitlines()
# total = 0
# weekday_total = [0, 0, 0, 0, 0, 0, 0]
# times= {}
# values = []
# to10 = 0
# for row in data:
#     if row[6] == "7":
#         day = (int(row[8:10])-1) % 7
#         nro = int(row.split(",")[1])
#         values.append(nro)
#         total+=nro
#         if nro > 8: to10+=1
#         weekday_total[day] += nro
#         if not row[11:13] in times: times[row[11:13]] = nro
#         else: times[row[11:13]]+=nro

# print(total)
# print(weekday_total)
# print(times)
# print(to10)
# print(average(values))

import datetime

t = datetime.datetime.now()
print(t.hour)