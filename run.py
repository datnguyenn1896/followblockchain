import requests
import time
import pandas as pd
from io import StringIO
import datetime

def craw_data():
    url = "https://api.whale-alert.io/feed.csv"
    payload = {}
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://whale-alert.io',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://whale-alert.io/',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return (response.text)

def add_to_array(array_seasion, seasion):
    # Kiểm tra nếu mảng có hơn 50 phần tử
    if len(array_seasion) >= 50:
        # Xóa phần tử đầu tiên
        array_seasion.pop(0)
    
    # Thêm phần tử mới vào cuối mảng
    array_seasion.append(seasion)
    return array_seasion

array_seasion = []

while(True):
    data = craw_data()
    # Tách dữ liệu thành từng dòng
    lines = data.strip().split("\n")

    # Xử lý từng dòng
    for line in lines:
        currency_data = []
        # Tách dòng thành các phần tử
        parts = line.split(',')
        timestamp = parts[1]
        # Chuyển đổi timestamp thành đối tượng datetime
        dt_object = datetime.datetime.fromtimestamp(int(timestamp))
        # Định dạng thời gian theo HH:MM:SS
        formatted_time = dt_object.strftime("%H:%M:%S")
        seasion = parts[0]
        currency = parts[2]
        volume = parts[3]
        price = float(parts[4])/float(parts[3])
        if parts[6] == '':
            from_user = parts[7]
        else:
            from_user = parts[6]
        if parts[8] == '':
            to_user = parts[9]
        else:
            to_user = parts[8]
        
        if (currency == "xrp" or currency == "xlm" or currency == "trx") and seasion not in array_seasion:
            print(parts)
            if from_user == "unknown" and to_user != "unknown" or from_user != "unknown" and to_user == "unknown":
                if from_user == "unknown" and to_user != "unknown":
                    type_transfer = "Sell"
                elif from_user != "unknown" and to_user == "unknown":
                    type_transfer = "Buy"
                add_to_array(array_seasion, seasion)
                print(formatted_time,currency,volume,price,from_user,to_user)
                currency_data.append([formatted_time, currency, volume, price, from_user,to_user, type_transfer])
                # Chuyển đổi danh sách thành DataFrame
                new_df = pd.DataFrame(currency_data, columns=['Time', 'Currency', 'Volume', 'Price', 'From User', 'To User', 'Type'])
                # Đọc file Excel đã tồn tại (nếu có)
                try:
                    # Nếu file đã tồn tại, đọc nó
                    existing_df = pd.read_excel('currency_data.xlsx')
                    # Thêm dữ liệu mới vào DataFrame hiện tại
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                except FileNotFoundError:
                    # Nếu file không tồn tại, tạo một DataFrame mới
                    combined_df = new_df

                # Lưu lại file Excel
                combined_df.to_excel('followblockchain/currency_data.xlsx', index=False)

    time.sleep(2)   