from pyats.topology import loader
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
file_handler = logging.FileHandler('log/Interface-CRC.log')
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

EOF = False
count_iface_up = 0
count_iface_down = 0
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

def proc_iface_crc(deviceX,counter):
    try:
        deviceX.connect(learn_hostname = True, learn_os = True, log_stdout=False)
        logger.info(f"Connecting to Device: {deviceX.name}")
        output_iface_crc = deviceX.parse('show interfaces')
        output_device = deviceX.parse('show inventory')
        for pid in output_device['main']['chassis']:
            devPID = pid
        for iface in output_iface_crc:
            crc = output_iface_crc[iface]['counters']['in_crc_errors']
            input_errors = output_iface_crc[iface]['counters']['in_errors']
            output_errors = output_iface_crc[iface]['counters']['out_errors']
            with open(
            f"out/InterfaceCRC/show_int_crc_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow([counter,deviceX.name, devPID,iface,crc,input_errors,output_errors])
   
    except Exception as e:
        logger.error(f"Error connecting to device {deviceX.name}: {e}")

def interfaceCRC(testbedFile):
    testbed= loader.load(testbedFile)
    with open(f'out/InterfaceCRC/show_int_crc_{timestamp}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['No','Hostname','Platform','Interface', 'CRC', 'Input Errors', 'Output Errors'])

                
    futures = []
    counter = 1

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            if device.type == 'iosxe':
                futures.append(executor.submit(proc_iface_crc, device, counter))
                counter += 1
                logger.info(f"getting CRC information from Device: {device.name}")
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
            logger.info(f"{exc} occurred while processing device {device.name}")

    logger.info("Script execution completed successfully.")

