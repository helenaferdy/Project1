from lib.getEnvi.router import Routers
import csv
import threading

CSV_PATH = "lib/getEnvi/device.csv"

def getEnvi():

    with open(CSV_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]

<<<<<<< HEAD

    # print('''
    # Welcome to helena network automation xxz
    # These are your devices : 
    # ''')
        
=======
>>>>>>> aa05144dc5b09034697ecdc17e7a57426bef14db
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

<<<<<<< HEAD
    commands_x = "show environment"
    headers = ['Hostname', 'Site', 'Power Supply', 'Temperature', 'Fan']
    try:
        with open(f"out/Environment/{commands_x}_summary.csv", mode="w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
    except:
        pass
=======
    command = "show environment"
    headers = ['Hostname', 'Site', 'Power Supply', 'Temperature', 'Fan']
 
    with open(f"out/Environment/{command}_summary.csv", mode="w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)

>>>>>>> aa05144dc5b09034697ecdc17e7a57426bef14db

    threads = []
    for device in devices:
        thread = threading.Thread(target=device.connect, args=(command,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

