from genie.testbed import load
from pyats.topology import loader
from datetime import datetime
from rich.console import Console
import os.path
from lib.log import myLog
import logging
from rich.logging import RichHandler
import traceback
import concurrent.futures
from time import sleep
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/CaptureConfig.log')
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
if not os.path.exists("out/CaptureConfig"):
    os.makedirs("out/CaptureConfig")


def captureConfigX(device):
    # Load the testbed file
    # Send a command to the device
    try:
        attempt = 1
        retry = 0
        mx_retry = 3
        while retry < mx_retry:
            try:
                device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
                break
            except Exception as conn_error:
                    retry += 1
                    attempt +=1
                    if retry < mx_retry:
                        logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
                        logger.info(f"Retrying in 1 seconds...")
                        time.sleep(2)
                    else:
                        logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
                        break  # Exit the loop after max retries
        #Print the output
        hostname = device.name
        logger.info('---getting capture config from device '+hostname+'---')
        waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
        NameFile = hostname + "_" + waktu +".txt"
        file_path = "out/CaptureConfig/"
        output = device.execute('show running-config')
        file_name = os.path.join(file_path,NameFile)
        logger.info(NameFile)
        try:
            with open(file_name, 'a') as file:
                file.write(f'''{output}''')
        except:
            logger.error("exception ",exc_info=1)
    except Exception as e:
        #print(f"Error connecting to device {device.name}: {e}")
        logger.error(f"Error connecting to device {device.name}: {e}")

def captureConfig(testbedFile):
    testbed = load(testbedFile)
    # Create a list of futures for iosxe and iosxr devices
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            futures.append(executor.submit(captureConfigX, device))
            logger.info(f"Connecting to device {device.name}")
            sleep(0.1)
        # Wait for all futures to complete

    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            logger.error(f"{exc} occurred while processing device {device.name}")
    logger.info("Get Config -  execution completed successfully.")