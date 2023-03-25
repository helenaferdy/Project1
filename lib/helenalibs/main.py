from lib.helenalibs.router import Routers, TIMESTAMP
import csv
import threading

CSV_PATH = "import/env.csv"

def helenamain(command, out):
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
        export_headers(headers, command, out)
    elif command == "show processes cpu":
        headers = ['No', 'Device', 'CPU Used', 'CPU Free', 'Category']
        export_headers(headers, command, out)
    elif command == "show inventory":
        headers = ['No', 'Hostname', 'Name', 'PID', 'SN']
        export_headers(headers, command, out)
    

    threads = []
    i = 1
    for device in devices:
        thread = threading.Thread(target=device.connect, args=(command, i))
        thread.start()
        threads.append(thread)
        i +=1

    for thread in threads:
        thread.join()


def export_headers(headers, command, out):
    with open(f"{out}{command}_summary_{TIMESTAMP}.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
