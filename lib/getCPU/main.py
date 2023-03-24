from pyats.topology.loader import load
import csv
import datetime
from genie.utils.timeout import Timeout
import logging
import concurrent.futures
from time import sleep
import logging
from rich.logging import RichHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/getCPUUtils.log')
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

# timeout = Timeout(max_time=10, interval=3)
# logging.basicConfig(level=logging.INFO)
cpu_load = 0

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

def xe(devicex, ix):
    resultx = {"no": ix,
               "device": devicex.name,
               "cpu_load": "",
               "free_load": "",
               "category": ""}

    try:
        devicex.connect(mit=True, log_stdout=False)
        output = devicex.parse('show processes cpu sorted | i CPU')
        cpu_load = output["five_min_cpu"]
        if cpu_load <= 40:
            category = 'low'
        elif cpu_load <= 70:
            category = 'medium'
        elif cpu_load <= 85:
            category = 'high'
        else:
            category = 'critical'

        free_load = str(100 - cpu_load) + '%'
        cpu_load = str(cpu_load) + '%'

        resultx = {"no": ix,
                   "device": devicex.name,
                   "cpu_load": cpu_load,
                   "free_load": free_load,
                   "category": category}
        # deviceX.disconnect()

        with open(f'out/CPU_Utils/show_processes_cpu_{timestamp}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            logger.info(f"{resultx['no']}, {resultx['device']}, {resultx['cpu_load']}, {resultx['free_load']}, {resultx['category']}")
            writer.writerow([resultx['no'], resultx['device'], resultx['cpu_load'], resultx['free_load'], resultx['category']])

    except Exception as e:
        if 'Authentication failed' in str(e):
            logger.error('Authentication failed. Please check your credentials.')
        elif 'Connection timed out' in str(e):
            logger.error('Connection timed out. Please check your network connectivity.')
        elif 'Could not connect to device' in str(e):
            logger.error('Could not connect to device. Please check the device is reachable.')
        else:
            logger.error(f'Unexpected error occurred: {str(e)}')

    return resultx


def xr(devicex, ix):
    resultx = {"no": ix,
               "device": devicex.name,
               "cpu_load": "",
               "free_load": "",
               "category": ""}

    try:
        devicex.connect(mit=True, log_stdout=False)
        output = devicex.parse('show processes cpu')
        cpu_load = output["location"]["node0_RP0_CPU0"]["five_min_cpu"]
        if cpu_load <= 40:
            category = 'low'
        elif cpu_load <= 70:
            category = 'medium'
        elif cpu_load <= 85:
            category = 'high'
        else:
            category = 'critical'

        free_load = str(100 - cpu_load) + '%'
        cpu_load = str(cpu_load) + '%'

        resultx = {"no": ix,
                   "device": devicex.name,
                   "cpu_load": cpu_load,
                   "free_load": free_load,
                   "category": category}
        # deviceX.disconnect()

        with open(f'out/CPU_Utils/show_processes_cpu_{timestamp}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            logger.info(f"{resultx['no']}, {resultx['device']}, {resultx['cpu_load']}, {resultx['free_load']}, {resultx['category']}")
            writer.writerow([resultx['no'], resultx['device'], resultx['cpu_load'], resultx['free_load'], resultx['category']])

    except Exception as e:
        if 'Authentication failed' in str(e):
            logger.error('Authentication failed. Please check your credentials.')
        elif 'Connection timed out' in str(e):
            logger.error('Connection timed out. Please check your network connectivity.')
        elif 'Could not connect to device' in str(e):
            logger.error('Could not connect to device. Please check the device is reachable.')
        else:
            logger.error(f'Unexpected error occurred: {str(e)}')


def getCPUUtils(testbed_file):
    testbed = load(testbed_file)
    with open(f'out/CPU_Utils/show_processes_cpu_{timestamp}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['No', 'Device', 'Memory Used', 'Memory Free', 'Category'])

        # i = 1
        # for device in testbed:
        #     print(f"===== processing {device.name} =====")
        #     if device.type == 'iosxe':
        #         final = xe(device, i)
        #         write = True
        #     elif device.type == 'iosxr':
        #         final = xr(device, i)
        #         write = True
        #         pass
        #
        #     if write:
        #         print(f"{final['no']}, {final['device']}, {final['cpu_load']}, {final['free_load']}, {final['category']}")
        #         writer.writerow([final['no'], final['device'], final['cpu_load'], final['free_load'], final['category']])
        #     i += 1

    futures = []
    i = 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            logger.info(f"===== processing {device.name} =====")
            if device.type == 'iosxe':
                futures.append(executor.submit(xe, device, i))
                i += 1
                sleep(0.1)
            elif device.type == 'iosxr':
                futures.append(executor.submit(xr, device, i))
                i += 1
                sleep(0.1)

        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            logger.error(f"{exc} occurred while processing device {device.name}")

    logger.info("Get CPU Utilization -  execution completed successfully.")