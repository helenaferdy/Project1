from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
import os
import csv
import logging, sys
import datetime

CONNECT_RETRY = 2
CUSTOM_FILE = "import/custom.txt"
TIMESTAMP = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
DATE = datetime.datetime.now().strftime('%Y-%m-%d')
os.environ["NTC_TEMPLATES_DIR"] = "lib/helenalibs/templates"

custom_commands = []
with open(CUSTOM_FILE, "r") as f:
    for csv_command in f:
        custom_commands.append(csv_command.strip())
        

class Routers:
    def __init__(self, hostname, ip, username, password, secret, ios_os, out, log_path):
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
        self.secret = secret
        self.ios_os = ios_os

        self.out_path = out
        self.date_path = out+DATE+"/"
        self.raw_path = self.date_path+"raw_data/"
        self.cpu_history_path = self.date_path+"history/"

        self.log_path = log_path
        self.errorlog_path = log_path[:-4]+"-error.log"

    def logging_info(self, message):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s', 
            handlers=[
                logging.FileHandler(self.log_path),
                logging.StreamHandler(sys.stdout)
                ])
        logging.info(message)
    
    def logging_error(self, message, e=""):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.errorlog_path, 'a') as f:
            f.write(f'{current_time} [ERROR] {message}\n')
            e_list = str(e).split("\n")
            e_list = [line for line in e_list if line.strip()]
            for line in e_list:
                f.write(f'{current_time} {line} \n')

    def connect(self, command, i):
        connected = False
        self.command = command
        self.i = i
        device = {
            "device_type": "cisco_ios",
            "ip": self.ip,
            "username": self.username,
            "password": self.password,
            "secret": self.secret,
        }
        
        self.logging_info(f"{self.ip} : Connecting ")
        retry = 0
        while retry < CONNECT_RETRY:
            if retry > 0:
                logging.info(f"{self.ip} : Retrying connection ")
            try:
                self.connection = ConnectHandler(**device)
                logging.info(f"{self.ip} : Connected ")
                retry = 2
                try:
                    self.connection.enable()
                    logging.info(f"{self.ip} : Entered enable mode ")
                    connected = True       
                except Exception as e:
                    err = (f"{self.ip} : Failed to enter enable mode")
                    logging.error(err)
                    self.logging_error(err, e)
            except Exception as e:
                retry +=1
                err = (f"{self.ip} : Failed to connect ({retry})")
                logging.error(err)
                self.logging_error(err, e)

        if connected and self.command != "custom":
            self.after_connect()
        elif connected and self.command == "custom":
            return True

    def after_connect(self):
        self.connect_command()
        if not os.path.exists(self.raw_path):
            os.makedirs(self.raw_path)
        if self.parse():
            self.export_csv()
            if self.command == "show environment":
                self.parse_environment_summary()
            elif self.command == "show processes cpu":
                self.parse_cpu_summary()
                #cpu history
                if not os.path.exists(self.cpu_history_path):
                    os.makedirs(self.cpu_history_path)
                self.command = self.command+" history"
                self.connect_command()
                self.parse_cpu_history()
            elif self.command == "show inventory":
                self.parse_inventory_summary()                            
        self.disconnect()

    def connect_command(self):
        try:
            self.output = self.connection.send_command(self.command)
            logging.info(f"{self.ip} : Command '{self.command}' sent")
        except Exception as e:
            err = (f"{self.ip} : Failed to parse command '{self.command}'")
            logging.error(err)
            self.logging_error(err, e)
    
    def parse(self):
        try:
            self.parsed_output = parse_output(platform=self.ios_os, command=self.command, data=self.output)
            if self.parsed_output == []:
                err = (f"{self.ip} : Parsed return empty for command '{self.command}'")
                logging.error(err)
                self.logging_error(err)
                return False
            else:
                logging.info(f"{self.ip} : Command '{self.command}' parsed")
                return True
        except Exception as e:
            err = (f"{self.ip} : Failed to parse command '{self.command}'")
            logging.error(err)
            self.logging_error(err, e)

    def export_csv(self):
        try:
            with open(f"{self.raw_path}{self.hostname}_{self.command}_{TIMESTAMP}.csv", mode="w", newline="") as csv_file:
                fieldnames = self.parsed_output[0].keys()
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.parsed_output:
                    writer.writerow(row)
            logging.info(f"{self.ip} : Output saved to {self.raw_path}{self.hostname}_{self.command}_{TIMESTAMP}.csv")
        except Exception as e:
            err = (f"{self.ip} : Failed saving to {self.raw_path}{self.hostname}_{self.command}_{TIMESTAMP}.csv")
            logging.error(err)
            self.logging_error(err, e)

    def disconnect(self):
        self.connection.disconnect()
        logging.info(f"{self.ip} : Disconnected succcessfully")


    # SUMMARY
    def parse_environment_summary(self):
        self.power = "OK"
        self.temp = "OK"
        self.fan = "OK"

        for p in self.parsed_output:
            if "pwr" in p['sensor']:
                if p['state'] != "Normal":
                    self.power = "NOK"
            elif "fan" in p['sensor']:
                if p['state'] != "Normal":
                    self.temp = "NOK"
            elif "Temp" in p['sensor']:
                if p['state'] != "Normal":
                    self.fan = "NOK"

        final_environment = [self.i ,self.hostname, "DC", self.power, self.fan, self.temp]
        self.export_csv_bonus(final_environment)

    def parse_cpu_summary(self):
        cpu_load = 0
        for p in self.parsed_output:
            cpu_load = int(p['cpu_5_min'])
            if cpu_load <= 40:
                category = 'LOW'
            elif cpu_load <= 70:
                category = 'MEDIUM'
            elif cpu_load <= 85:
                category = 'HIGH'
            else:
                category = 'CRITICAL'

        free_load = str(100 - cpu_load) + '%'
        cpu_load = str(cpu_load) + '%'
        
        final_cpu = [self.i, self.hostname, cpu_load, free_load, category]
        self.export_csv_bonus(final_cpu)

    def parse_cpu_history(self):
        try:
            with open(f"{self.cpu_history_path}{self.hostname}_{self.command}_{TIMESTAMP}.txt", mode="w", newline="") as txtfile:
                txtfile.write(self.output)
                logging.info(f"{self.ip} : Output saved to {self.cpu_history_path}{self.hostname}_{self.command}_{TIMESTAMP}.txt")
        except Exception as e:
            err = (f"{self.ip} : Failed saving to {self.cpu_history_path}{self.hostname}_{self.command}_{TIMESTAMP}.txt")
            logging.error(err)
            self.logging_error(err, e)
    
    def parse_inventory_summary(self):
        i = 1
        for p in self.parsed_output:
            name = p['name']
            pid = p['pid']
            sn = p['sn']

            final_inventory = [i, self.hostname, name, pid, sn]
            self.export_csv_bonus(final_inventory)
            i +=1
            
    def export_csv_bonus(self, final):
        try:
            with open(f"{self.date_path}{self.command}_summary_{TIMESTAMP}.csv", mode="a", newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(final)
                logging.info(f"{self.ip} : Output appended to {self.date_path}{self.hostname}_{self.command}_summary_{TIMESTAMP}.csv")
        except Exception as e:
            err = (f"{self.ip} : Failed appending for {self.date_path}{self.hostname}_{self.command}_summary_{TIMESTAMP}.csv")
            logging.error(err)
            self.logging_error(err, e)


    ## CUSTOM COMMAND    
    def custom_connect(self):
        if self.connect("custom", 0):
            for c in custom_commands:
                self.command = c
                self.connect_command()
                if "Invalid" in self.output:
                    err = (f"{self.ip} : Invalid command '{self.command}'")
                    logging.error(err)
                    self.logging_error(err)
                self.export_custom_command()
            self.disconnect()

    def export_custom_command(self):
        try:
            with open(f"{self.date_path}{self.ip}_custom_{TIMESTAMP}.txt", mode="a") as txtfile:
                txtfile.write('\n---------------------------------------------------------------------------\n')
                txtfile.write(self.command)
                txtfile.write('\n---------------------------------------------------------------------------\n')
                txtfile.write(self.output)
                txtfile.write('\n---------------------------------------------------------------------------\n\n\n')
                logging.info(f"{self.ip} : Output appended to {self.date_path}{self.ip}_custom_{TIMESTAMP}.txt")
        except Exception as e:
            err = (f"{self.ip} : Failed appending to {self.date_path}{self.ip}_custom_{TIMESTAMP}.txt")
            logging.error(err)
            self.logging_error(err, e)