from datetime import datetime

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

# 

if __name__ == '__main__': do_monthly_analysis(7)