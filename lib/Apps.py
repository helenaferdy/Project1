import subprocess
from pathlib import Path
import time
import pyfiglet
import pyinputplus as pyip
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt
import sys
from lib.log import myLog
from datetime import datetime
from lib.getConfig.main import captureConfig
from lib.getMemmory.main_backup import getMemmoryUtils
from lib.getCPU.main import getCPUUtils
from lib.getLogging.main import captureLog
import logging
from rich.logging import RichHandler

console = Console()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/Application.log')
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


Menu = ['Get Configuration Device','Get Inventory Device','Get Memmory Utils','Get CPU Utils','Get Logging Device','Get All','Exit']

testbedFile = 'testbed/device.yaml'


def create():
    console.print("If you want to import csv/xls/xlsx, please put into folder 'import'")
    input_str = Prompt.ask("Please input name file csv/xls/xlsx, you want to import (ex :filename.csv)")

    # Start Bash script as subprocess with input from variable
    result = subprocess.Popen(['/bin/bash', './lib/createTestbed.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Send input to subprocess and get output and errors
    output, errors = result.communicate(input=input_str.encode())

    # Get return code
    return_code = result.returncode

    if return_code == 0:
        # Success
        logger.info("Importing file..."+input_str)
        for i in track(range(100), description="Progress..."):
            time.sleep(0.01)

        logger.info(f"Success: {output.decode().strip()}")
        logger.info("---testbed file ready---")
        return True
    elif return_code == 1:
        # Error
        logger.error(f"Error: {errors.decode().strip()}")
        return False

def check():
    # check path file is exsist or not, return True / False
    path = Path(testbedFile)
    return path.is_file()

def init():
    logger.info("---Starting the Application---")
    ascii_banner = pyfiglet.figlet_format("MasterSystem - ProjectOne")
    console.print(ascii_banner,style="Bold Red")
    logger.info("---Initialize testbed file---")
    if check() == False:
        logger.warning("---System can't find testbed file---")
        time.sleep(0.5)
        if create() == False:
          return False
        
    else:
        logger.info("---testbed file ready---")
        updateFile = pyip.inputYesNo(prompt="Do you want to update testbed file..? (Y/n)",blank=False)
        if updateFile == 'yes':
            if create() == False:
                return False
        time.sleep(0.5)
        logger.info("---Opening Main Menu Application---")
        time.sleep(1)
    return True
        
    
def MainMenu():
    console.print("--Main Menu--",style="Bold Green")
    menuResponse=pyip.inputMenu(Menu,numbered=True,blank=False,prompt="Please select one of the following menu..?\n")
    print(menuResponse)
    if(menuResponse=='Get Configuration Device'):
        logger.info("---Get Configuration Device---")

        #### add function get Config device here ####
        captureConfig(testbedFile)
        
    elif(menuResponse=='Get Inventory Device'):
        logger.info("---Get Inventory Device---")

        #### add function get Inventory Device here ####

        
    elif(menuResponse=='Get Memmory Utils'):
        logger.info("---Get Memmory Utilization---")

        #### function get Memmory Utilization ####
        getMemmoryUtils(testbedFile)
        
    elif(menuResponse=='Get CPU Utils'):
        logger.info("---Get CPU Utilization---")

        #### function get CPU Utilization ####
        getCPUUtils(testbedFile)
        
        
    elif(menuResponse=='Get Logging Device'):
        logger.info("---Get Logging device---")
        
        #### function get Logging device ####
        captureLog(testbedFile)
        
    elif(menuResponse=='Get All'):
        logger.info("---Get All---")
        #### function get all ####
        logger.info("---Get Configuration Device---")
        captureConfig(testbedFile)
        logger.info("---Get Memmory Utilization---")
        getMemmoryUtils(testbedFile)
        logger.info("---Get CPU Utilization---")
        getCPUUtils(testbedFile)
        logger.info("---Get Logging device---")
        captureLog(testbedFile)

        
    elif(menuResponse=='Exit'):
        logger.info("---Closing Application---")
        time.sleep(1)
        sys.exit()