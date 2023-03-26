from lib.helenalibs.router import Routers, TIMESTAMP, DATE
import csv
import threading
import os

CSV_PATH = "import/env.csv"

def helenamain(command, out):
    date_path = out+DATE+"/"
    if not os.path.exists(date_path):
            os.makedirs(date_path)

    with open(CSV_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]
    

    with open(CSV_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]
    
    print('Devices : \n')
    devices = []
    for d in data:
        print(f"{d['hostname']} : {d['ip']}")
        new_router = Routers(
            d['hostname'],
            d['ip'],
            d['username'],
            d['password'],
            d['enable_password'],
            d['os'],
            out
        )
        devices.append(new_router)
        
    if command == "show environment":
        headers = ['No','Hostname', 'Site', 'Power Supply', 'Temperature', 'Fan']
        export_headers(headers, command, date_path)
    elif command == "show processes cpu":
        headers = ['No', 'Device', 'CPU Used', 'CPU Free', 'Category']
        export_headers(headers, command, date_path)
    elif command == "show inventory":
        headers = ['No', 'Hostname', 'Name', 'PID', 'SN']
        export_headers(headers, command, date_path)
    

    threads = []
    i = 1
    for device in devices:
        thread = threading.Thread(target=device.connect, args=(command, i))
        thread.start()
        threads.append(thread)
        i +=1

    for thread in threads:
        thread.join()


def export_headers(headers, command, date_path):
    with open(f"{date_path}{command}_summary_{TIMESTAMP}.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
