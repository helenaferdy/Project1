import os
import csv
import datetime
import concurrent.futures
from time import sleep
from pyats.topology.loader import load
import logging
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

# Check if output folder is available, create it if not
if not os.path.exists("out/MemmoryUtils"):
    os.makedirs("out/MemmoryUtils")

# Load the topology from the YAML file

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def get_iosxe_memory_info(device, counter):
    try:
        # Connect to the device
        device.connect(mit=True, log_stdout=False)

        # Print the output
        logger.info(f"Device: {device.name}")

        output = device.parse("show memory statistics")

        used = round(output["name"]["processor"]["used"]/1024/1000, 2)
        total = round(output["name"]["processor"]["total"]/1024/1000, 2)
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
            f"out/MemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])

        return counter

    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

def get_iosxr_memory_info(device, counter):
    try:
        # Connect to the device
        device.connect(mit=True, log_stdout=False)

        # Print the output
        logger.info(f"Device: {device.name}")

        output = device.parse("show watchdog memory-state")

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
            f"out/MemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{counter}", f"{device.name}", used_memory_mb, physical_memory_mb, percentage, category])

        return counter

    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

def get_ios_memory_info(device, counter):
    try:
        # Connect to the device
        device.connect(mit=True, log_stdout=False)

        # Print the output
        logger.info(f"Device: {device.name}")

        output = device.parse("show memory statistics")

        used = round(output["name"]["processor"]["used"]/1024/1000, 2)
        total = round(output["name"]["processor"]["total"]/1024/1000, 2)
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
            f"out/MemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])

        return counter

    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

def get_nxos_memory_info(device, counter):
    try:
        # Connect to the device
        device.connect(mit=True, log_stdout=False)

        # Print the output
        logger.info(f"Device: {device.name}")

        output = device.parse("show system resources")

        used = round(output["memory"]["used"]/1024, 2)
        total = round(output["memory"]["total"]/1024, 2)
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
            f"out/MemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])

        return counter

    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")


def getMemmoryUtils(testbedFile):
    testbed = load(testbedFile)
    # Open the output file in append mode
    with open(f"out/MemmoryUtils/summary_show_memory_{timestamp}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(["No", "Device", "Memory Used in MB", "Memory Total in MB", "Percentage", "Category"])

    # Create a list of futures for iosxe and iosxr devices
    futures = []
    counter = 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            if device.type == 'iosxe':
                futures.append(executor.submit(get_iosxe_memory_info, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'iosxr':
                futures.append(executor.submit(get_iosxr_memory_info, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'ios':
                futures.append(executor.submit(get_ios_memory_info, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'ios':
                futures.append(executor.submit(get_nxos_memory_info, device, counter))
                counter += 1
                sleep(0.1)
            else:
                futures.append(executor.submit(get_ios_memory_info, device, counter))
                counter += 1
                sleep(0.1)
        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            logger.error(f"{exc} occurred while processing device {device.name}")

    logger.info("Get Memmory Utilization - execution completed successfully.")

# Define functions to retrieve memory information for iosxe and iosxr devices