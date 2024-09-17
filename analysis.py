from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas

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

def dataplot():
    fname = "2024-08-28"
    data = pandas.read_csv('data.csv')
    coffee = data[data.columns[1]].to_numpy()
    w = 10
    avg_coffee = np.convolve(coffee, np.ones(w), 'valid') / w
    times = data[data.columns[0]].to_numpy()
    ttimes = []
    for t in times:
        ttimes.append(datetime.strptime(t[:19], '%Y-%m-%d %H:%M:%S'))
    # print(ttimes)
    F = plt.figure ()
    plt.plot (coffee , 'b')
    plt.savefig(f"smooth.png")


if __name__ == '__main__': dataplot()