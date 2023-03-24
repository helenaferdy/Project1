from lib.getEnvi.router import Routers
import csv
import threading

CSV_PATH = "lib/getEnvi/device.csv"

def getEnvi():

    with open(CSV_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]


    # print('''
    # Welcome to helena network automation xxz
    # These are your devices : 
    # ''')
        
    devices = []
    for d in data:
        print(f"{d['hostname']} : {d['ip']}")
        new_router = Routers(
            d['hostname'],
            d['ip'],
            d['username'],
            d['password'],
            d['enable']
        )
        devices.append(new_router)

    commands_x = "show environment"
    headers = ['Hostname', 'Site', 'Power Supply', 'Temperature', 'Fan']
    try:
        with open(f"out/Environment/{commands_x}_summary.csv", mode="w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
    except:
        pass

    threads = []
    for device in devices:
        thread = threading.Thread(target=device.connect, args=(commands_x,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

