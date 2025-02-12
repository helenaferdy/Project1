from lib.getCustom.device import Routers, TIMESTAMP, ERROR_COMMAND
import csv
import threading
import os
import yaml

TEMPLATE_NUMBERS = 7

TITLE = "getEnvironment"
COMMAND1 = "show environment"
COMMAND2 = "show env all"
HEADERS = ['No','Hostname', 'Site', 'Power Supply', 'Temperature', 'Fan']
TESTBED =  "testbed/device.yaml"
devices = []
success_counter = []
fail_counter = []

def main(testbed):
    read_testbed()
    export_headers()
    i = 1
    threads = []
    for device in devices:
        t = threading.Thread(target=process_device, args=(device, i))
        t.start()
        threads.append(t)
        i += 1

    for t in threads:
        t.join()
    
    sort_csv()
    end_summary()

def process_device(device, i):
    parsed = ""
    num_try = 0
    device.command_template = COMMAND1
    device.out_path = f"out/{TITLE}/"
    device.log_path = f"log/{TITLE}.log"
    device.errorlog = f"log/error/{TITLE}-error.log"
    device.create_folder()
    if device.connect(i):
        command = COMMAND1
        output = "Function exception"
        while output == "Function exception" and device.exception_counter < 3:
            output = device.connect_command(command)

        #try other command
        if [c for c in ERROR_COMMAND if c in output]:
            device.logging_error(f"{device.hostname} : Command [{command}] Failed, trying [{COMMAND2}]")
            command = COMMAND2
            output = device.connect_command(command)
        
        #final check output
        if [c for c in ERROR_COMMAND if c in output]:
            device.logging_error(f"{device.hostname} : Output return empty for command [{command}]")
        else:
            while parsed == "" and num_try < TEMPLATE_NUMBERS:
                num_try += 1
                parsed = device.parse(COMMAND1, output, num_try)
        
        #special templates
        if parsed != "":
            if num_try <= 3:
                ## special templates 1, 2, 3
                final = export_csv_3(parsed, i, device.hostname)
                device.export_data(final)
            elif num_try > 3 and num_try <= TEMPLATE_NUMBERS:
                ## regular templates
                final = export_csv(parsed, i, device.hostname)
                device.export_data(final)
            else:
                ## no templates, insert generic values
                final = export_desperate(i, device.hostname)
                device.export_data(final)
            success_counter.append(0)
        else:
            device.logging_error(f"{device.hostname} : Parsing failed after [{num_try}] tries.")
            final = export_desperate(i, device.hostname)
            device.export_data(final)
            fail_counter.append(f'{device.ip} - {device.ios_os} - {device.hostname}')

        device.disconnect()
    else:
        fail_counter.append(f'{device.ip} - {device.ios_os} - {device.hostname}')

def export_headers():
    outpath = f'out/{TITLE}/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    with open(f"{outpath}{COMMAND1}_{TIMESTAMP}.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)

def read_testbed():
    with open(TESTBED) as f:
        device = yaml.safe_load(f)['devices']
        for d in device:
            the_ip = device[d]['connections']['cli']['ip']
            the_protocol = device[d]['connections']['cli']['protocol']
            the_username = device[d]['credentials']['default']['username']
            the_password = device[d]['credentials']['default']['password']
            the_enable = device[d]['credentials']['enable']['password']
            the_ios_os = device[d]['os']

            new_device = Routers(
                d,
                the_ip,
                the_username,
                the_password,
                the_enable,
                the_ios_os,
                the_protocol
            )
            devices.append(new_device)

def end_summary():
    print(f'\n=> Success : [{len(success_counter)}/{len(devices)}]\n')
    if len(fail_counter) > 0:
        print(f'=> Failed  :')
        for idx, fc in enumerate(fail_counter):
            print(f'   {idx+1}. {fc}')
        print('')


#general template
def export_csv(parsed, i, hostname):
    power = "OK"
    temp = "OK"
    fan = "OK"

    for p in parsed:
        if "pwr" in p['sensor']:
            if p['state'] != "Normal":
                power = "NOK"
        elif "fan" in p['sensor']:
            if p['state'] != "Normal":
                temp = "NOK"
        elif "Temp" in p['sensor']:
            if p['state'] != "Normal":
                fan = "NOK"

    final = [i, hostname, "DC", power, fan, temp]
    return final

#template no 1, 2, 3
def export_csv_3(parsed, i, hostname):
    power = "OK"
    temp = "OK"
    fan = "OK"

    for p in parsed:
        if p['temp'] != "":
            temp = p['temp'] 
        if p['fan'] != "":
            fan = p['fan']

    final = [i, hostname, "DC", power, fan, temp]
    return final

def export_desperate(i, hostname):
    power = ""
    temp = ""
    fan = ""

    final = [i, hostname, "", power, fan, temp]
    return final

def sort_csv():
    outpath = f'out/{TITLE}/'
    sort_field="No"
    data = []
    
    try:
        # Read the data from the input CSV file
        with open(f"{outpath}{COMMAND1}_{TIMESTAMP}.csv", "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

        # Sort the data based on the specified field
        sorted_data = sorted(data, key=lambda x: int(x.get(sort_field, 0)))

        # Write the sorted data back to the input CSV file
        with open(f"{outpath}{COMMAND1}_{TIMESTAMP}.csv", "w", newline="") as csvfile:
            fieldnames = sorted_data[0].keys() if sorted_data else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_data)

    except Exception as e:
        print(f"Failed sorting {e}")