from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler,NetmikoTimeoutException, NetmikoAuthenticationException, ConnectionException
import getpass
# import logging
from lib.File import SFMRead,ReadFile
import os
from datetime import datetime

class AutoPy:
    credential = {}
    data = []

    def SetUserPass(user,pwd,sec,iteration):
        AutoPy.credential[iteration] = {'user':user,'pass':pwd, 'sec':sec}

    def SetListCredential(self,list_credential):
        #### Get Credential List from user ####
        for list in range(list_credential):
            print(f"Setup number {list+1} from {list_credential}, credential details")
            usr = input('Please entered your username..? ')
            pwd = getpass.getpass(prompt='Please entered your password..? ')
            sec = getpass.getpass(prompt='Please entered your enable secret..? ')
            AutoPy.SetUserPass(usr,pwd,sec,list)
        #### End Get Credential List from user ####

    def ConnectDevice(self,ip,cmd,menu,**user):
        try:
            date_now   = datetime.now()
            time_stamp = date_now.strftime("%d-%m-%y_%H_%M")
            # print(ip,kwargs)
            # print(kwargs)
            print(f"Connecting to device: {ip}, with credential {user['user']}")
            remote_device = {
                        'device_type': 'autodetect',
                        'host': ip,
                        'username': user['user'],
                        'password': user['pass'],
                        'secret': user['sec']
                        }
            # print(remote_device)
            guesser = SSHDetect(**remote_device)
            best_match = guesser.autodetect()
            # print(best_match)
            remote_device['device_type'] = best_match
            # print(remote_device)
            connection = ConnectHandler(**remote_device)
            connection.enable()
            print(f"Connected with device: {ip}, with credential {user['user']}")
            getHostname = connection.send_command("sh run | i hostname")
            hostname = getHostname.split()

            if menu==1:
                dir = "./out/captureConfig"
                isExist = os.path.exists(dir)
                if not isExist:
                    os.makedirs(dir)

                file_path = "./"+dir+"/"

                hostname_date = hostname[1] + '-' + time_stamp + '.txt'
                file_name = os.path.join(file_path, hostname_date)

                print(f"Capturing Config device: {ip}, with credential {user['user']}")
                for val in cmd:
                    getInfoDevice = connection.send_command(val)
                    with open(file_name, 'a') as file:
                        file.write(f'''\n{val}\n{getInfoDevice}\n\n''')
            elif menu==5:
                dir = "./out/captureLog"
                isExist = os.path.exists(dir)
                if not isExist:
                    os.makedirs(dir)

                file_path = "./"+dir+"/"

                hostname_date = hostname[1] + '-' + time_stamp + '.log'
                file_name = os.path.join(file_path, hostname_date)
                print(f"Capturing Logging device: {ip}, with credential {user['user']}")
                for val in cmd:
                    getInfoDevice = connection.send_command(val)
                    with open(file_name, 'a') as file:
                        file.write(f'''\n{val}\n{getInfoDevice}\n\n''')
            else:
                for val in cmd:
                    getInfoDevice = connection.send_command(val)

                result = SFMRead(getInfoDevice,best_match,cmd)

                if result != False:
                    if menu == 2:
                        print(f"Capturing Inventory device: {ip}")
                        for dataDevice in result:
                            AutoPy.data.append([hostname[1],'',dataDevice['NAME'],dataDevice['DESCR'],'',dataDevice['SN']])
                    elif menu == 3:
                        print(f"Capturing Memmory Utilization device: {ip}")
                        for dataDevice in result:
                            memUsed = int(dataDevice['MEMORY_USED'])/(1024*1024)
                            memTotal = int(dataDevice['MEMORY_TOTAL'])/(1024*1024)
                            percent = (memUsed/memTotal)*100
                            if percent <= 20:
                                status = 'LOW'
                            elif percent <= 40:
                                status = 'MEDIUM'
                            elif percent <= 60:
                                status = 'HIGH'
                            elif percent > 60:
                                status = 'CRITICAL'
                            AutoPy.data.append([hostname[1],'',int(memUsed),int(memTotal),int(percent),status])
                    elif menu == 4:
                        print(f"Capturing CPU Utilization device: {ip}")
                        for dataDevice in result:
                            cpu = int(dataDevice['CPU_5_MIN'])
                            if cpu <= 20:
                                status = 'LOW'
                            elif cpu <= 40:
                                status = 'MEDIUM'
                            elif cpu <= 60:
                                status = 'HIGH'
                            elif cpu > 60:
                                status = 'CRITICAL'
                            AutoPy.data.append([hostname[1],'',cpu,status])
            # return data
        except NetmikoTimeoutException as error:
            # print(f"Error: "+str(error))
            msg = False
            return msg
        except NetmikoAuthenticationException as error:
            # print(f"Error: "+str(error))
            msg = False
            return msg
        except ConnectionException as error:
            # print(f"Error: "+str(error))
            msg = False
            return msg
        
