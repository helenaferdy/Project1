from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
import os
import csv
import logging, sys
import datetime

LOG_LOCATION = "lib/helenalibs/logs/debug.log"
TIMESTAMP = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
DATE = datetime.datetime.now().strftime('%Y-%m-%d')
os.environ["NTC_TEMPLATES_DIR"] = "lib/helenalibs/templates"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s', 
    handlers=[
        logging.FileHandler(LOG_LOCATION),
        logging.StreamHandler(sys.stdout)
        ])

class Routers:
    def __init__(self, hostname, ip, username, password, secret, ios_os, out):
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

        if not os.path.exists(self.raw_path):
            os.makedirs(self.raw_path)
        

    def connect(self, command, i):
        allgood = False
        self.command = command
        self.i = i
        device = {
            "device_type": "cisco_ios",
            "ip": self.ip,
            "username": self.username,
            "password": self.password,
            "secret": self.secret,
        }
        try:
            self.connection = ConnectHandler(**device)
            logging.info(f"{self.ip} : Connected ")
            try:
                self.connection.enable()
                logging.info(f"{self.ip} : Entered enable mode ")
                allgood = True
            except Exception as e:
                logging.error(f"{self.ip}: Failed to enter enable mode")
        except Exception as e:
            logging.error(f"{self.ip}: Failed to connect")

        if allgood:
            self.connect_command()
            if self.parse():
                self.export_csv()
                if self.command == "show environment":
                    self.parse_environment_summary()
                elif self.command == "show processes cpu":
                    self.parse_cpu_summary()

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
            logging.error(f"{self.ip} : Failed to parse command '{self.command}'")
    
    def parse(self):
        try:
            self.parsed_output = parse_output(platform=self.ios_os, command=self.command, data=self.output)
            logging.info(f"{self.ip} : Command '{self.command}' parsed")
            return True
        except Exception as e:
            logging.error(f"{self.ip} : Failed to parse command '{self.command}'")

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
            logging.error(f"{self.ip} : Failed saving to {self.raw_path}{self.hostname}_{self.command}_{TIMESTAMP}.csv")

    def disconnect(self):
        self.connection.disconnect()
        logging.info(f"{self.ip} : Disconnected succcessfully")


    # bonus +++
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
        except:
            logging.error(f"{self.ip} : Failed saving to {self.cpu_history_path}{self.hostname}_{self.command}_{TIMESTAMP}.txt")
    
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
            logging.error(f"{self.ip} : Failed appending for {self.date_path}{self.hostname}_{self.command}_summary_{TIMESTAMP}.csv")