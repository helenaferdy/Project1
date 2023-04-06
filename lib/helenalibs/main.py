from lib.helenalibs.router import Routers, TIMESTAMP, DATE
import csv
import threading
import os
import yaml

# CSV_PATH = "import/env.csv"
TESTBED =  "testbed/device.yaml"

def helenamain(command, out, log_path):
    date_path = out+DATE+"/"
    if not os.path.exists(date_path):
            os.makedirs(date_path)

    devices = []
    with open(TESTBED) as f:
        device = yaml.safe_load(f)['devices']
        for d in device:
            the_ip = device[d]['connections']['cli']['ip']
            the_protocol = device[d]['connections']['cli']['protocol']
            the_username = device[d]['credentials']['default']['username']
            the_password = device[d]['credentials']['default']['password']
            the_enable = device[d]['credentials']['enable']['password']
            the_ios_os = device[d]['os']
            the_log_path = log_path

            print(f"{d} : {the_ip}")
            new_router = Routers(
                d,
                the_ip,
                the_username,
                the_password,
                the_enable,
                the_ios_os,
                out,
                the_log_path
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
