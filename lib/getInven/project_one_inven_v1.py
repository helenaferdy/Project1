from genie.testbed import load
import yaml
import csv

# Constants:
TEST_BED_FILE = "testbed_pyats_supark.yml"
OUTPUT_INVEN_FILE = "myinven.csv"
OUTPUT_VER_FILE = "myver.csv"
OUTPUT_INT_FILE = "myint.csv"

# TODO: Create function to import list of equipments from CSV and generate test-bed YAML. Format: hostname, ip, username, password. Optional: os_type, protocol.
# TODO: Rewrite program using OOP.

def create_device_dict(input_file_name):
    """FUNCTION: Create two dictionaries from test bed: for IOS-XR and IOS-XE."""
    output_dict_xr = {}
    output_dict_xe = {}
    with open(input_file_name, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print (exc)
    
    for x in parsed_yaml["devices"]:
        if parsed_yaml["devices"][x]["os"] == "iosxr":
            output_dict_xr[x] = parsed_yaml["devices"][x]["os"]
        elif parsed_yaml["devices"][x]["os"] == "iosxe":
            output_dict_xe[x] = parsed_yaml["devices"][x]["os"]

    return output_dict_xr, output_dict_xe


def parse_inven_xr(input_test_bed, input_dict):
    """FUNCTION: Create Inventory List for IOS XR."""
    output_list = []
    for rtr in input_dict:
        print(f"{rtr}: Connecting... ", end="")
        dev = input_test_bed.devices[rtr]
        dev.connect(learn_hostname = True, learn_os = True, mit = True, log_stdout = False)
        print("OK. Parsing... ", end="")
        sh_inven_parsed = dev.parse("show inventory")
        x = []
        for i in sh_inven_parsed["module_name"]:
            x.append(i)
        for i in x:
            col1 = str(rtr)
            col2 = str(i)
            col3 = str(sh_inven_parsed["module_name"][i]["pid"])
            col4 = str(sh_inven_parsed["module_name"][i]["sn"])
            output_list.append([col1,col2,col3,col4])
        print("Complete.")
    return output_list


def parse_inven_xe(input_test_bed, input_dict):
    """FUNCTION: Create Inventory List for IOS XE."""
    output_list = []
    for rtr in input_dict:
        print(f"{rtr}: Connecting... ", end="")
        dev = input_test_bed.devices[rtr]
        dev.connect(learn_hostname = True, learn_os = True, mit = True, log_stdout = False)
        print("OK. ",end="")
        print("Parsing... ", end="")
        sh_inven_parsed = dev.parse("show inventory")
        for i in sh_inven_parsed["main"]["chassis"]:
            col1 = str(rtr)
            col2 = str(sh_inven_parsed["main"]["chassis"][i]["name"])
            col3 = str(sh_inven_parsed["main"]["chassis"][i]["pid"])
            col4 = str(sh_inven_parsed["main"]["chassis"][i]["sn"])
            output_list.append([col1,col2,col3,col4])

        for i in sh_inven_parsed["slot"]:
            for j in sh_inven_parsed["slot"][i]:
                for k in sh_inven_parsed["slot"][i][j]:
                    col1 = rtr
                    col2 = str(sh_inven_parsed["slot"][i][j][k]["name"])
                    col3 = str(sh_inven_parsed["slot"][i][j][k]["pid"])
                    col4 = str(sh_inven_parsed["slot"][i][j][k]["sn"])
                    output_list.append([col1,col2,col3,col4])
        print("Complete.")
    return output_list


def write_inven_csv(file_name, input_list_1, input_list_2):
    """FUNCTION: Write inventory list to CSV file with defined file name."""    
    with open (file_name, "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["hostname","name","pid","sn"])

        for x in input_list_1:
            writer.writerow(x)
        for x in input_list_2:
            writer.writerow(x)


#Populate device dictionary:
test_bed = load(TEST_BED_FILE)
device_dict_xr, device_dict_xe = create_device_dict(TEST_BED_FILE)
# print(device_dict_xr) # debugger
# print(device_dict_xe) # debugger

print("Parsing inventory IOS-XR:")
inventory_list_xr = parse_inven_xr(test_bed, device_dict_xr)
print("Done.")

print("Parsing inventory IOS-XE:")
inventory_list_xe = parse_inven_xe(test_bed, device_dict_xe)
print("Done.")

print("Creating CSV: ", end="")
write_inven_csv(OUTPUT_INVEN_FILE, inventory_list_xr, inventory_list_xe)
print("Complete.")
