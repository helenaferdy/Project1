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
from lib.getMemmory.main import getMemmoryUtils
from lib.getCPU.main import main as getCPUUtils
from lib.getLogging.main import captureLog
from lib.getCRC.main import interfaceCRC
from lib.getInven.main import main as getInven
from lib.getCDP.main import main as  getCDP
from lib.getEnvi.main import main as  getEnvi
from lib.getCustom.main import main as  getCustom
from lib.NetworkTopology.main import main as  NetworkTopology
import logging
from rich.logging import RichHandler
import concurrent.futures
from time import sleep

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


Menu = ['Get Configuration Device','Get Inventory Device','Get Memory Utils','Get CPU Utils','Get Logging Device','Get Interface CRC','Get CDP Neighbours','Get Environtment','Get Custom Commands', 'Create Network Topology' ,'Exit']

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
    menuResponse=pyip.inputMenu(Menu,allowRegexes=[r'([0-9]+(,[0-9]+)+)'],blockRegexes=[r'([0-9][0-9]+(,[0-9][0-9]+)+)'],numbered=True,blank=False,prompt="Please select one or multiple (separate by comma ',') of the following menu..?\n")
    # console.print(menuResponse)
    if(menuResponse.find(',')==True):
        input = menuResponse.split(',')
        futures = []
        counter = 1
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for val in input:
                futures.append(executor.submit(inputMenu, val))
                logger.info("Proccesing menu: "+ Menu[int(val)-1])
                counter += 1
                sleep(0.1)
        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                logger.error(f"{exc} occurred while processing")
    else:
        inputMenu(menuResponse)
    

def inputMenu(value):
    if(value==Menu[0] or value=='1'):
        logger.info("---Get Configuration Device---")

        #### add function get Config device here ####
        captureConfig(testbedFile)
        
    elif(value==Menu[1] or value=='2'):
        logger.info("---Get Inventory Device---")
        
        #### add function get Inventory Device here ####
        getInven(testbedFile)

        
    elif(value==Menu[2] or value=='3'):
        logger.info("---Get Memmory Utilization---")

        #### function get Memmory Utilization ####
        getMemmoryUtils(testbedFile)
        
    elif(value==Menu[3] or value=='4'):
        logger.info("---Get CPU Utilization---")

        #### function get CPU Utilization ####
        getCPUUtils(testbedFile)
           
    elif(value==Menu[4] or value=='5'):
        logger.info("---Get Logging device---")
        
        #### function get Logging device ####
        captureLog(testbedFile)

    elif(value==Menu[5] or value=='6'):
        logger.info("---Get Interface CRC device---")
        
        #### function get Logging device ####
        interfaceCRC(testbedFile)

    elif(value==Menu[6] or value=='7'):
        logger.info("---Get CDP Neighbours ---")
        
        #### function get Logging device ####
        getCDP(testbedFile)
    
    elif(value==Menu[7] or value=='8'):
        logger.info("---Get Healty Check / Environtment Device ---")
        
        #### function get Logging device ####
        getEnvi(testbedFile)

    elif(value==Menu[8] or value=='9'):
        logger.info("---Get Custom Commands from txt ---")
        
        #### function get Logging device ####
        getCustom(testbedFile)
        
    elif(value==Menu[9] or value=='10'):
        logger.info("---Create Network Topology ---")
        
        #### function get Logging device ####
        NetworkTopology()

    elif(value==Menu[10] or value=='11'):
        logger.info("---Closing Application---")
        time.sleep(1)
        sys.exit()
    else:
        logger.info("--Error Input menu--")