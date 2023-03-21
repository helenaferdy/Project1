from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
import os
import csv
import logging, sys

LOG_LOCATION = "log/getEnvironment.log"
os.environ["NTC_TEMPLATES_DIR"] = "/Users/helena/Documents/VSCode/netmiko-network-automation/templates"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s', 
    handlers=[
        logging.FileHandler(LOG_LOCATION),
        logging.StreamHandler(sys.stdout)
        ])

class Routers:
    def __init__(self, hostname, ip, username, password, secret):
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
        self.secret = secret

    def connect(self, command):
        allgood = False
        self.command = command
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
            self.disconnect()

    def connect_command(self):
        try:
            self.output = self.connection.send_command(self.command)
            logging.info(f"{self.ip} : Command '{self.command}' sent")
        except Exception as e:
            logging.error(f"{self.ip} : Command '{self.command}' failed")
    
    def parse(self):
        try:
            self.parsed_output = parse_output(platform="cisco_ios", command=self.command, data=self.output)
            logging.info(f"{self.ip} : Command '{self.command}' parsed")
            return True
        except Exception as e:
            logging.error(f"{self.ip} : Command '{self.command}' failed to parse")

    def export_csv(self):
        try:
            with open(f"output/{self.hostname}_{self.command}.csv", mode="w", newline="") as csv_file:
                fieldnames = self.parsed_output[0].keys()
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.parsed_output:
                    writer.writerow(row)
            logging.info(f"{self.ip} : Output saved to {self.hostname}_{self.command}.csv")
        except Exception as e:
            logging.error(f"{self.ip} : Output saving for {self.command} failed")

    def disconnect(self):
        self.connection.disconnect()
        logging.info(f"{self.ip} : Disconnected succcessfully")

    
    # bonus ++
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

        self.final_environment = [self.hostname, "DC", self.power, self.fan, self.temp]
        try:
            with open(f"output/{self.command}_summary.csv", mode="a", newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.final_environment)
                logging.info(f"{self.ip} : Output saved to {self.command}_summary.csv")
        except Exception as e:
            logging.error(f"{self.ip} : Output saving for {self.command} summary failed")
