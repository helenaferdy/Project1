from pyats.topology.loader import load
import csv
import datetime




def xe(deviceX, iX):
    deviceX.connect(mit=True, log_stdout=False)
    output = deviceX.parse('show processes cpu sorted | i CPU')

    cpu_load = output["five_min_cpu"]
    if cpu_load <= 40:
        category = 'low'
    elif cpu_load <= 70:
        category = 'medium'
    elif cpu_load <= 85:
        category = 'high'
    else:
        category = 'critical'

    free_load = str(100 - cpu_load)+'%'
    cpu_load = str(output["five_min_cpu"])+'%'

    resultX = {"no": iX,
               "device": deviceX.name,
               "cpu_load": cpu_load,
               "free_load": free_load,
               "category": category}

    return resultX

def getCPUUtils(testbedfile):
    testbed = load(testbedfile)

    write = False
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    with open(f'out/CPU_Utils/processes_cpu_{timestamp}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['No', 'Device', 'Memory Used', 'Memory Free', 'Category'])

        i = 1
        for device in testbed:
            print(f"===== processing {device.name} =====")
            if device.type == 'iosxe':
                final = xe(device, i)
                write = True
            elif device.type == 'iosxr':
                pass

            if write:
                print(f"{final['no']}, {final['device']}, {final['cpu_load']}, {final['free_load']}, {final['category']}")
                writer.writerow([final['no'], final['device'], final['cpu_load'], final['free_load'], final['category']])
            i += 1