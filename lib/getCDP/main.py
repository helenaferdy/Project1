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


# Check if output folder is available, create it if not
if not os.path.exists("out/CDP"):
    os.makedirs("out/CDP")

def proc_cdp_ios(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, mit=True, log_stdout=False)
        output = device.parse('show cdp neighbors')
        logger.info(f"Device: {device.name}")
        for data in output['cdp']['index'].values():
            with open(
            f"out/CDP/show_cdp_neigh_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow([counter,device.name, data['local_interface'],data['device_id'],data['port_id'],data['platform']])
        return counter
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

def proc_cdp_xe(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, mit=True, log_stdout=False)
        output = device.parse('show cdp neighbors')
        logger.info(f"Device: {device.name}")
        for data in output['cdp']['index'].values():
            with open(
            f"out/CDP/show_cdp_neigh_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow([counter,device.name, data['local_interface'],data['device_id'],data['port_id'],data['platform']])
        return counter
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")
     
def proc_cdp_xr(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, mit=True, log_stdout=False)
        output = device.parse('show cdp neighbors')
        logger.info(f"Device: {device.name}")
        for data in output['cdp']['index'].values():
            with open(
            f"out/CDP/show_cdp_neigh_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow([counter,device.name, data['local_interface'],data['device_id'],data['port_id'],data['platform']])
        return counter
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")
     
def proc_cdp_nx(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, mit=True, log_stdout=False)
        output = device.parse('show cdp neighbors')
        logger.info(f"Device: {device.name}")
        for data in output['cdp']['index'].values():
            with open(
            f"out/CDP/show_cdp_neigh_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow([counter,device.name, data['local_interface'],data['device_id'],data['port_id'],data['platform']])
        return counter
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

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
                futures.append(executor.submit(proc_cdp_xe, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'iosxr':
                futures.append(executor.submit(proc_cdp_xr, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'nxos':
                futures.append(executor.submit(proc_cdp_nx, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'ios':
                futures.append(executor.submit(proc_cdp_ios, device, counter))
                counter += 1
                sleep(0.1)
        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            logger.error(f"{exc} occurred while processing device {device.name}")

    logger.info("Script execution completed successfully.")
