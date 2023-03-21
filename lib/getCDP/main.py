from pyats.topology import loader
import os
import csv
import datetime
import concurrent.futures
from time import sleep
import logging
from rich.logging import RichHandler
from rich.console import Console

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/CDP-Neighbours.log')
shell_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
# the formatter determines what our logs will look like
fmt_shell = '%(message)s'
fmt_file = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

shell_formatter = logging.Formatter(fmt_shell)
file_formatter = logging.Formatter(fmt_file)

# here we hook everything together
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)
logger.addHandler(shell_handler)
logger.addHandler(file_handler)

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

def proc_cdp(deviceX,counter):
    try:
        deviceX.connect(learn_hostname = True, learn_os = True, mit=True, log_stdout=False)
        logger.info(f"Connecting to Device: {deviceX.name}")
        output = deviceX.parse('show cdp neighbors')
        output_device = deviceX.parse('show inventory')
        for pid in output_device['main']['chassis']:
            devPID = pid
            
        for data in output['cdp']['index'].values():
            with open(f'out/CDP/show_cdp_neigh_{timestamp}.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([deviceX.name, data['local_interface'],devPID,data['device_id'],data['port_id'],data['platform']])
    except Exception as e:
        print(f"Error connecting to device {deviceX.name}: {e}")
     
    return counter   

def getCDP(testbedFile):
    testbed= loader.load(testbedFile)
    with open(f'out/CDP/show_cdp_neigh_{timestamp}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['NE Hostname','NE Interface', 'NE Platform', 'FE Hostname', 'FE Interface', 'FE Platform'])
        

        # for device in testbed:
        #     print(f"===== processing {device.name} =====") 
        #     final = proc_cdp(device)
            
    futures = []
    counter = 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            if device.type == 'iosxe':
                futures.append(executor.submit(proc_cdp, device, counter))
                counter += 1
                logger.info(f"getting CDP neighbours information from Device: {device.name}")
                sleep(0.1)
            # elif device.type == 'iosxr':
            #     futures.append(executor.submit(get_iosxr_memory_info, device, counter))
            #     counter += 1
            #     sleep(0.1)
        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            print(f"{exc} occurred while processing device {device.name}")

    print("Script execution completed successfully.")
