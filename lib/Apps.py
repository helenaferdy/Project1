import pyinputplus as pyip
import sys
from lib.File import ReadFile,DataFrame,ProcessExcel
import lib.Automation as auto
import pyfiglet
# from multiprocessing.dummy import Pool, Process

def MainMenu():
    ascii_banner = pyfiglet.figlet_format("Welcome")
    print(ascii_banner)
    print("Main Menu Application")
    menuResponse=pyip.inputMenu(['Get Configuration Device','Get Inventory Device','Get Memmory Utils','Get CPU Utils','Get Logging Device','Exit'],numbered=True,prompt="Please select one of the following menu..?\n")
    if(menuResponse=='Get Configuration Device'):
        getConfig()
    elif(menuResponse=='Get Inventory Device'):
        getInven()
    elif(menuResponse=='Get Memmory Utils'):
        getMemUtils()
    elif(menuResponse=='Get CPU Utils'):
        getCPUUtils()
    elif(menuResponse=='Get Logging Device'):
        getLogging()
    elif(menuResponse=='Exit'):
        sys.exit()

def getConfig():
    menu = 1
    cmd=['show run']
    getConfigDevice = auto.AutoPy()
    try:
        list_credential = pyip.inputNum(prompt='How many you have the credential..(1-3)? ',min=1,max=3,limit=3)
    except pyip.RetryLimitException:
        print("Error: Retry Limit exception")
        sys.exit()
    
    getConfigDevice.SetListCredential(list_credential)
    # print(getConfigDevice.credential)
    listIP = ReadFile("ListIP","txt","r")
    if listIP != None:
        Prompt = "you have "+str(len(listIP))+" device IP in the list, are you sure..(yes/no)?  "
        confirm_listIP = pyip.inputYesNo(prompt=Prompt)
        if confirm_listIP =="yes":
            ################# Serial Processs #################
            for ip in listIP:
                for user in range(len(getConfigDevice.credential)):
                    device = getConfigDevice.ConnectDevice(ip,cmd,menu,**getConfigDevice.credential[user])
                    if device != False:
                        print("OK")
                        break
            ################# End Serial Processs #################
    else:
        print("Please update file ListIP")
        sys.exit()
    print("Get Config Device, Success")
    MainMenu()

def getInven():
    menu = 2
    cmd=['show inventory']
    getInvenDevice = auto.AutoPy()
    try:
        list_credential = pyip.inputNum(prompt='How many you have the credential..(1-3)? ',min=1,max=3,limit=3)
    except pyip.RetryLimitException:
        print("Error: Retry Limit exception")
        sys.exit()
    
    getInvenDevice.SetListCredential(list_credential)
    # print(getInvenDevice.credential)
    listIP = ReadFile("ListIP","txt","r")
    if listIP != None:
        Prompt = "you have "+str(len(listIP))+" device IP in the list, are you sure..(yes/no)?  "
        confirm_listIP = pyip.inputYesNo(prompt=Prompt)
        if confirm_listIP =="yes":
            ################# Serial Processs #################
            for ip in listIP:
                for user in range(len(getInvenDevice.credential)):
                    device = getInvenDevice.ConnectDevice(ip,cmd,menu,**getInvenDevice.credential[user])
                    if device != False:
                        print("OK")
                        break
            ################# End Serial Processs #################

            ################# Multiprocess Processs #################
            # for user in range(len(credential)):
            #     device = [Process(target=ConnectDevice, args=[ip] , kwargs=credential[user]) for ip in listIP]
            #     print(f"{device}")
            #     # start all processes
            #     for process in device:
            #         process.start()
            #     # wait for all processes to complete
            #     for process in device:
            #         process.join()
                
            #     if device!=False:
            #         print('Done', flush=True)
            #         break
            ################# End Multiprocess Processs #################

            DataFrame(getInvenDevice.data,menu)
            ProcessExcel(nameFile='DeviceInventory')
    else:
        print("Please update file ListIP")
        sys.exit()
    print("Get Inventory Device, Success")
    MainMenu()

def getMemUtils():
    menu = 3
    cmd=['show processes memory sorted']
    getMemUtilsDevice = auto.AutoPy()
    try:
        list_credential = pyip.inputNum(prompt='How many you have the credential..(1-3)? ',min=1,max=3,limit=3)
    except pyip.RetryLimitException:
        print("Error: Retry Limit exception")
        sys.exit()
    
    getMemUtilsDevice.SetListCredential(list_credential)
    # print(getInvenDevice.credential)
    listIP = ReadFile("ListIP","txt","r")
    if listIP != None:
        Prompt = "you have "+str(len(listIP))+" device IP in the list, are you sure..(yes/no)?  "
        confirm_listIP = pyip.inputYesNo(prompt=Prompt)
        if confirm_listIP =="yes":
            ################# Serial Processs #################
            for ip in listIP:
                for user in range(len(getMemUtilsDevice.credential)):
                    device = getMemUtilsDevice.ConnectDevice(ip,cmd,menu,**getMemUtilsDevice.credential[user])
                    if device != False:
                        print("OK")
                        break
            ################# End Serial Processs #################
        DataFrame(getMemUtilsDevice.data,menu)
        ProcessExcel(nameFile='MemmoryUtils')
    else:
        print("Please update file ListIP")
        sys.exit()
    print("Get Memmory Utils Device, Success")
    MainMenu()

def getCPUUtils():
    menu = 4
    cmd=['show processes cpu platform']
    getCpuUtilsDevice = auto.AutoPy()
    try:
        list_credential = pyip.inputNum(prompt='How many you have the credential..(1-3)? ',min=1,max=3,limit=3)
    except pyip.RetryLimitException:
        print("Error: Retry Limit exception")
        sys.exit()
    
    getCpuUtilsDevice.SetListCredential(list_credential)
    # print(getInvenDevice.credential)
    listIP = ReadFile("ListIP","txt","r")
    if listIP != None:
        Prompt = "you have "+str(len(listIP))+" device IP in the list, are you sure..(yes/no)?  "
        confirm_listIP = pyip.inputYesNo(prompt=Prompt)
        if confirm_listIP =="yes":
            ################# Serial Processs #################
            for ip in listIP:
                for user in range(len(getCpuUtilsDevice.credential)):
                    device = getCpuUtilsDevice.ConnectDevice(ip,cmd,menu,**getCpuUtilsDevice.credential[user])
                    if device != False:
                        print("OK")
                        break
            ################# End Serial Processs #################
        DataFrame(getCpuUtilsDevice.data,menu)
        ProcessExcel(nameFile='CPU-Utils')
    else:
        print("Please update file ListIP")
        sys.exit()
    print("Get CPU Utils Device, Success")
    MainMenu()

def getLogging():
    menu = 5
    cmd=['show logging']
    getConfigDevice = auto.AutoPy()
    try:
        list_credential = pyip.inputNum(prompt='How many you have the credential..(1-3)? ',min=1,max=3,limit=3)
    except pyip.RetryLimitException:
        print("Error: Retry Limit exception")
        sys.exit()
    
    getConfigDevice.SetListCredential(list_credential)
    # print(getConfigDevice.credential)
    listIP = ReadFile("ListIP","txt","r")
    if listIP != None:
        Prompt = "you have "+str(len(listIP))+" device IP in the list, are you sure..(yes/no)?  "
        confirm_listIP = pyip.inputYesNo(prompt=Prompt)
        if confirm_listIP =="yes":
            ################# Serial Processs #################
            for ip in listIP:
                for user in range(len(getConfigDevice.credential)):
                    device = getConfigDevice.ConnectDevice(ip,cmd,menu,**getConfigDevice.credential[user])
                    if device != False:
                        print("OK")
                        break
            ################# End Serial Processs #################
    else:
        print("Please update file ListIP")
        sys.exit()
    print("Get Logging Device, Success")
    MainMenu()