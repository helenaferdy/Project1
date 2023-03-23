from lib.getEnvi.router import Routers
import csv
import threading

CSV_PATH = "lib/getEnvi/device.csv"

def getEnvi():

    with open(CSV_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]

    devices = []
    for d in data:
        print(f"{d['hostname']} : {d['ip']}")
        new_router = Routers(
            d['hostname'],
            d['ip'],
            d['username'],
            d['password'],
            d['enable_password']
        )
        devices.append(new_router)

    command = "show environment"
    headers = ['Hostname', 'Site', 'Power Supply', 'Temperature', 'Fan']
 
    with open(f"out/Environment/{command}_summary.csv", mode="w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)


    threads = []
    for device in devices:
        thread = threading.Thread(target=device.connect, args=(command,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

