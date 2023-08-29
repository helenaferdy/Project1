import concurrent.futures
import csv
import datetime
import logging
import os
import time
from time import sleep

import textfsm
from netmiko import (ConnectHandler, NetMikoAuthenticationException,
                     NetMikoTimeoutException)
from pyats.topology.loader import load
from pyats.utils.secret_strings import to_plaintext
from rich.logging import RichHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/getMemmoryUtils.log')
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

#Create timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

#Function to sorted data
def sort_csv_by_field(input_file, sort_field):
    data = []
    
    # Read the data from the input CSV file
    with open(input_file, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    # Sort the data based on the specified field
    sorted_data = sorted(data, key=lambda x: int(x.get(sort_field, 0)))

    # Write the sorted data back to the input CSV file
    with open(input_file, "w", newline="") as csvfile:
        fieldnames = sorted_data[0].keys() if sorted_data else []
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_data)

##Funtion to write error logs
def write_error_log(message):
    log_directory = "log/error"
    log_file = "Error-getMemoryUtils.log"
    log_path = os.path.join(log_directory, log_file)

    # Create the log directory if it doesn't exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Write the error message to the log file
    with open(log_path, "a") as f:
        f.write(message + "\n")

#function to convert tesbed device into netmiko format
def convert_to_netmiko(device):
    netmiko_device = {}
    netmiko_device['device_type'] = "cisco_ios"
    netmiko_device['host'] = str(device.connections.cli.ip)
    netmiko_device['username'] = device.credentials.default.username
    netmiko_device['password'] = to_plaintext(device.credentials.default.password)
    netmiko_device['secret'] = to_plaintext(device.credentials.enable.password)
    return netmiko_device

def get_iosxe_memory_info(device, counter):
    pyats_bypass_test = False
    try:
        try:
            if pyats_bypass_test == True:
                raise Exception
            attempt = 1
            retry = 0
            mx_retry = 3
            while retry < mx_retry:
                try:
                    logger.info(f"Initiate connection to Device {device.name} attempt {attempt}")
                    device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
                    # Print the output
                    logger.info(f"Device: {device.name} Connected Successfully")
                    #send command
                    try:
                        output = device.parse("show processes memory")
                        logger.info(f"Parse Device: {device.name} Data Successfully")    
                    except:
                        logger.error(f"Failed to Parse Device: {device.name} using Pyats IOSXE Function")
                        write_error_log(f"Failed to Parse Device: {device.name} using Pyats IOSXE Function")
                    break  # Exit the loop if connected successfully
                except Exception as conn_error:
                    retry += 1
                    attempt +=1
                    if retry < mx_retry:
                        logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
                        logger.info(f"Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
                        write_error_log(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
                        break  # Exit the loop after max retries
            
            #mapped parse data
            used = round(output['processor_pool']['used']/1024/1000, 2)
            total = round(output['processor_pool']['total']/1024/1000, 2)
            percentage = round(used / total * 100, 2)

            # Categorize percentage based on certain ranges
            if percentage <= 40:
                category = "low"
            elif percentage <= 70:
                category = "medium"
            elif percentage <= 85:
                category = "high"
            else:
                category = "critical"
            # Write the output to the CSV file
            with open(
                f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])
        except:
            logger.error(f"Failed to Connect Using Main Function pyats iosxe for {device.name} try Nemiko IOSXE Function")
            write_error_log(f"Failed to Connect Using Main Function pyats iosxe for {device.name} try Nemiko IOSXE Function")
            
            # Convert the device to Netmiko format            
            netmiko_device = convert_to_netmiko(device)
            
            # Initiate connection max 3 
            retries = 0
            max_retries = 3
            retry_interval = 2
            while retries < max_retries:
                try:
                    logger.info(f"Establishing Connection for {netmiko_device['host']} using Netmiko IOSXE Function")
                    connection = ConnectHandler(**netmiko_device)
                    logger.info(f"Connection Success for {netmiko_device['host']} using Netmiko IOSXE Function")
                    return connection
                except (NetMikoAuthenticationException, NetMikoTimeoutException) as auth_error:
                    logger.error(f"Authentication or connection error (attempt {retries+1}/{max_retries}) for device {netmiko_device['host']}: {auth_error}")
                    retries += 1
                    if retries < max_retries:
                        logger.info(f"Retrying {netmiko_device['host']} in {retry_interval} seconds...")
                        time.sleep(retry_interval)
                    else:
                        logger.error(f"Maximum retries reached. Unable to establish connection to device {netmiko_device['host']} using IOSXE Netmiko Function")
                        write_error_log((f"Maximum retries reached. Unable to establish connection to device {netmiko_device['host']} using IOSXE Netmiko Function"))
                        return None
            # Send a command and retrieve the output
            command = "show processes memory"
            output = connection.send_command(command)

            with open('lib/getMemmory/ios_xe_switch.template') as template:
                template = textfsm.TextFSM(template)
            try:
                # Parse the command output using the template
                parsed_output = template.ParseText(output)
                logger.info(f"Success Parse Data for {netmiko_device['host']} using Netmiko IOSXE Function")
            except:
                logger.error(f"Failed to Parse Data for {netmiko_device['host']} using Netmiko IOSXE Function")

            header = template.header
            used_index = header.index('used')
            total_index = header.index('total')
            free_index = header.index('free')

            # Extract the values from the parsed output
            used = round(int(parsed_output[0][used_index])/1024, 2)
            total = round(int(parsed_output[0][total_index])/1024, 2)
            free = round(int(parsed_output[0][free_index])/1024 , 2)
            percentage = round(used / total * 100, 2)

            #categorize data
            if percentage <= 40:
                category = "low"
            elif percentage <= 70:
                category = "medium"
            elif percentage <= 85:
                category = "high"
            else:
                category = "critical"
            #write data
            with open(
                        f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
                    ) as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])
        return counter
    except Exception as e:
        logger.error(f"Error connecting or gather device {device.name}: {e} using Pyats or Netmiko fucntion")
        write_error_log(f"Error connecting or gather device {device.name}: {e} using Pyats or Netmiko fucntion")
def get_iosxr_memory_info(device, counter):
    try:
        attempt = 1
        retry = 0
        mx_retry = 3
        while retry < mx_retry:
            try:
                logger.info(f"Initiate connection to Device {device.name} attempt {attempt}")
                device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
                # Print the output
                logger.info(f"Device: {device.name} Connected Successfully")
                #send command
                try:
                    output = device.parse("show watchdog memory-state")
                    logger.info(f"Parse Device: {device.name} Data Successfully")
                except:
                    logger.error(f"Failed to Parse Device: {device.name}")
                    write_error_log(f"Failed to Parse Device: {device.name}")
                break  # Exit the loop if connected successfully
            except Exception as conn_error:
                retry += 1
                attempt +=1
                if retry < mx_retry:
                    logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
                    logger.info(f"Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts using IOSXR Pyats Function.")
                    write_error_log(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts using IOSXR Pyats Function.")
                    break  # Exit the loop after max retries

        physical_memory_mb = output["node"]["node0_RP0_CPU0"]["physical_memory_mb"]
        free_memory_mb = output["node"]["node0_RP0_CPU0"]["free_memory_mb"]
        used_memory_mb = physical_memory_mb - free_memory_mb
        percentage = round(used_memory_mb / physical_memory_mb * 100, 2)

        # Categorize percentage based on certain ranges
        if percentage <= 40:
            category = "low"
        elif percentage <= 70:
            category = "medium"
        elif percentage <= 85:
            category = "high"
        else:
            category = "critical"

        # Write the output to the CSV file
        with open(
            f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{counter}", f"{device.name}", used_memory_mb, physical_memory_mb, percentage, category])
        return counter
    except Exception as e:
        logger.error(f"Error connecting or gather device {device.name} using IOSXR Pyats Function")
        write_error_log(f"Error connecting or gather device {device.name} using IOSXR Pyats Function")
def get_ios_memory_info(device, counter):
    try:
        attempt = 1
        retry = 0
        mx_retry = 3
        while retry < mx_retry:
            try:
                logger.info(f"Initiate connection to Device {device.name} attempt {attempt}")
                device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
                # Print the output
                logger.info(f"Device: {device.name} Connected Successfully")
                #send command
                try:
                    output = device.parse("show processes memory")
                    logger.info(f"Parse Device: {device.name} Data Successfully")
                except:
                    logger.error(f"Failed to Parse Device: {device.name} using Pyats IOS Function.")
                    write_error_log(f"Failed to Parse Device: {device.name} using Pyats IOS Function.")
                break  # Exit the loop if connected successfully
            except Exception as conn_error:
                retry += 1
                attempt +=1
                if retry < mx_retry:
                    logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
                    logger.info(f"Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts using Pyats IOS Function.")
                    write_error_log(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts using Pyats IOS Function.")
                    break  # Exit the loop after max retries
        #parse data
        used = round(output['processor_pool']['used']/1024/1000, 2)
        total = round(output['processor_pool']['total']/1024/1000, 2)
        percentage = round(used / total * 100, 2)

        # Categorize percentage based on certain ranges
        if percentage <= 40:
            category = "low"
        elif percentage <= 70:
            category = "medium"
        elif percentage <= 85:
            category = "high"
        else:
            category = "critical"

        # Write the output to the CSV file
        with open(
            f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])
        return counter
    except Exception as e:
        logger.error(f"Error connecting or gather device {device.name} Pyats IOS Function")
        write_error_log(f"Error connecting or gather device {device.name} Pyats IOS Function")
        
def get_nxos_memory_info(device, counter):
    pyats_bypass_test = False
    try:
        try:
            if pyats_bypass_test == True:
                raise Exception
            attempt = 1
            retry = 0
            mx_retry = 3
            # Connect to the device
            while retry < mx_retry:
                try:
                    logger.info(f"Initiate connection to Device {device.name} attempt {attempt}")
                    device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
                    logger.info(f"Device: {device.name} Connected Successfully")
                    #send command
                    try:
                        output = device.parse("show system resources")
                        logger.info(f"Parse Device: {device.name} Data Successfully")
                    except:
                        logger.error(f"Failed to Parse Device: {device.name} using Pyats NXOS Function")
                        write_error_log(f"Failed to Parse Device: {device.name} using Pyats NXOS Function")
                    break  # Exit the loop if connected successfully
                except Exception as conn_error:
                    retry += 1
                    attempt +=1
                    if retry < mx_retry:
                        logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
                        logger.info(f"Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts using NXOS Function.")
                        write_error_log(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts using NXOS Function.")
                        break  # Exit the loop after max retries
            #parse data
            used = round(output["memory_usage"]["memory_usage_used_kb"]/1024, 2)
            total = round(output["memory_usage"]["memory_usage_total_kb"]/1024, 2)
            percentage = round(used / total * 100, 2)

            # Categorize percentage based on certain ranges
            if percentage <= 40:
                category = "low"
            elif percentage <= 70:
                category = "medium"
            elif percentage <= 85:
                category = "high"
            else:
                category = "critical"

            # Write the output to the CSV file
            with open(
                f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])
            return counter
        except:
            logger.error(f"Failed to Connect Using Main Function Pyats NSOX for {device.name}")
            write_error_log(f"Failed to Connect Using Main Function Pyats NSOX for {device.name}")
            # Convert the device to Netmiko format
            netmiko_device = convert_to_netmiko(device)

            # Initiate connection max 3 times with interval 2 second
            retries = 0
            max_retries = 3
            retry_interval = 2
            while retries < max_retries:
                try:
                    logger.info(f"Establishing connection for {netmiko_device['host']} using Netmiko NXOS Function")
                    connection = ConnectHandler(**netmiko_device)
                    logger.info(f"Device: {device.name} Connected Successfully using Netmiko NXOS Function")
                    return connection
                except (NetMikoAuthenticationException, NetMikoTimeoutException) as auth_error:
                    logger.error(f"Authentication or connection error (attempt {retries+1}/{max_retries}) for device {netmiko_device['host']}: {auth_error}")
                    retries += 1
                    if retries < max_retries:
                        logger.info(f"Retrying {netmiko_device['host']} in {retry_interval} seconds...")
                        time.sleep(retry_interval)
                    else:
                        logger.error(f"Maximum retries reached. Unable to establish connection to device {device.name} Using Netmiko NSOX Function.")
                        write_error_log(f"Maximum retries reached. Unable to establish connection to device {device.name} Using Netmiko NSOX Function.")
                        return None
            # Send a command and retrieve the output
            command = "show system resources"
            output = connection.send_command(command)

            with open('lib/getMemmory/nxos.template') as template:
                template = textfsm.TextFSM(template)
            try:
                # Parse the command output using the template
                parsed_output = template.ParseText(output)
                logger.info(f"Parse Device: {device.name} Data using Netmiko NXOS Function Successfully")
            except:
                logger.error(f"Failed to Parse Device: {device.name} using Netmiko NXOS Function")
                write_error_log(f"Failed to Parse Device: {device.name} using Netmiko NXOS Function")
            header = template.header
            used_index = header.index('used')
            total_index = header.index('total')
            free_index = header.index('free')

            # Extract the values from the parsed output
            used = round(int(parsed_output[0][used_index])/1024, 2)
            total = round(int(parsed_output[0][total_index])/1024, 2)
            free = round(int(parsed_output[0][free_index])/1024 , 2)
            percentage = round(used / total * 100, 2)

            # Categorize Data
            if percentage <= 40:
                category = "low"
            elif percentage <= 70:
                category = "medium"
            elif percentage <= 85:
                category = "high"
            else:
                category = "critical"
            with open(
                        f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
                    ) as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])       
        return counter
    except Exception as e:
        logger.error(f"Error connecting or gather device {device.name} using Pyats or Netmiko fucntion")
        write_error_log(f"Error connecting or gather device {device.name} using Pyats or Netmiko fucntion")

def getMemmoryUtils(testbedFile):
    #Check if output folder is available, create it if not
    if not os.path.exists("out/getMemmoryUtils"):
        os.makedirs("out/getMemmoryUtils")

    # Load the topology from the YAML file
    testbed = load(testbedFile)
    # Open the output file in append mode
    with open(f"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(["No", "Device", "Memory Used in MB", "Memory Total in MB", "Percentage", "Category"])
    # Define csv name for sorted purpose
    input_csv = (F"out/getMemmoryUtils/summary_show_memory_{timestamp}.csv")
    sort_field = "No"

    # Create a list of futures for multi thread proccess
    futures = []
    counter = 1
    #count device
    total_device = 0
    ios_xe_device = 0
    ios_xr_device = 0
    nxos_device = 0
    ios_device = 0
    #count failed device
    failed_iosxr = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for device in testbed:
            if device.type == 'iosxe':
                futures.append(executor.submit(get_iosxe_memory_info, device, counter))
                counter += 1
                ios_xe_device += 1
                total_device+=1
                sleep(0.1)
            elif device.type == 'iosxr':
                futures.append(executor.submit(get_iosxr_memory_info, device, counter))
                counter += 1
                ios_xr_device += 1
                total_device+=1
                sleep(0.1)
            elif device.type == 'ios':
                futures.append(executor.submit(get_ios_memory_info, device, counter))
                counter += 1
                ios_device += 1
                total_device+=1
                sleep(0.1)
            elif device.type == 'nxos':
                futures.append(executor.submit(get_nxos_memory_info, device, counter))
                counter += 1
                nxos_device += 1
                total_device+=1
                sleep(0.1)
        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
            #sort the output data
        except Exception as exc:
            logger.error(f"{exc} occurred while processing device {device.name}")
    logger.info("Get Memmory Utilization - execution completed.")
    #Sorted the output data
    sort_csv_by_field(input_csv, sort_field)
    logger.info("Sort Output Data - execution completed.")
    logger.info(f"Total Executed Get Memory Device is IOS_XE:{ios_xe_device} IOS_XR:{ios_xr_device} IOS:{ios_device} NXOS:{nxos_device} and Total Device is {total_device}")