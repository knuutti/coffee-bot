from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas
import matplotlib.dates as mdates

def do_monthly_analysis(month: int):
    hour_amounts = [0] * 24
    file = open('brew_data.csv', 'r')
    monthly_data = file.read().splitlines()
    brew_amounts = []
    for data_point in monthly_data:
        time_stamp, amount = data_point.split(',')
        date = datetime.strptime(time_stamp[0:19], '%Y-%m-%d %H:%M:%S')
        print(date.month)
        if date.month == month:
            amount = int(amount)
            brew_amounts.append(amount)
            hour_amounts[date.hour] += amount
    print(hour_amounts)
    print("Kahvia keitettiin", len(brew_amounts), "kertaa")
    return

def day_graph():
    data = pandas.read_csv('data.csv')
    coffee = data[data.columns[1]].to_numpy()
    times = data[data.columns[0]].to_numpy()
    hist = 10 * [coffee[0]]
    ttimes = []
    ccoffee = []
    for t in times:
        ttimes.append(datetime.strptime(t[:19], '%Y-%m-%d %H:%M:%S'))
    for c in coffee:
        hist.pop(0)
        hist.append(c)
        ccoffee.append(sum(hist)/10)

    plt.figure()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel("time")
    plt.ylabel("coffee level")
    plt.plot (ttimes, ccoffee , 'b')
    plt.title(f'Coffee data ({times[0][0:10]})')
    plt.savefig("day_graph.png")

    return None

def do_daily_analysis():
    hour_amounts = [0] * 24
    file = open('brew_data.csv', 'r')
    daily_data = file.read().splitlines()
    total_brews = len(daily_data)
    brew_amounts = []
    for data_point in daily_data:
        time_stamp, amount = data_point.split(',')
        date = datetime.strptime(time_stamp[0:19], '%Y-%m-%d %H:%M:%S')
        amount = int(amount)
        brew_amounts.append(amount)
        hour_amounts[date.hour] += amount
    print(hour_amounts)
    return


if __name__ == '__main__':
    day_graph()
