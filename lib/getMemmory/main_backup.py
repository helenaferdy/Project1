from pyats.topology.loader import load
import csv
import datetime


def getMemmoryUtils(testbedFile):
    # Load the topology from the YAML file
    testbed = load(testbedFile)

    # Open the output file in append mode
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    with open(f'out/MemmoryUtils/memory_statistics_{timestamp}.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header row
        writer.writerow(['No', 'Device', 'Memory Used', 'Memory Total', 'Percentage', 'Category'])
        
        # Loop through the devices in the topology
        counter = 1
        for device in testbed:
            # Connect to the device
            device.connect(mit=True, log_stdout=False)

            #Print the output
            print(f"Device: {device.name}")

            output = device.parse('show memory statistics')
            
            used = output['name']['processor']['used']
            total = output['name']['processor']['total']
            percentage = round(used / total * 100, 2)  # Round percentage to 2 decimal places
            
            # Categorize percentage based on certain ranges
            if percentage <= 40:
                category = 'low'
            elif percentage <= 70:
                category = 'medium'
            elif percentage <= 85:
                category = 'high'
            else:
                category = 'critical'

            # Write the output to the CSV file
            writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])
            
            counter += 1