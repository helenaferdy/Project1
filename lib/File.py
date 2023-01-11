import textfsm , os
import pandas as pd
from datetime import datetime

def ReadFile(nameFile,typeFile,typeAction):
    """Function untuk membaca list IP / Command device dari file"""
    with open("import/"+nameFile+"."+typeFile, typeAction) as listFile:
        result = listFile.read().split("\n")
        if result == ['']:
            print("Error : No value in this file or file is empty")
        else:
            return result
           
def SFMRead(var,type,action):
    """Function untuk membaca template custom TextSFM"""
    listCmd = ReadFile('cmdList','txt','r')
    res = any((match := item) in action for item in listCmd)
    cmd = match.replace(" ","_")
    if res == True:
        file = "./lib/Template/"+type+"_"+cmd+".template"
        with open(file) as template:
            fsm = textfsm.TextFSM(template)
            result = fsm.ParseTextToDicts(var)
            return result
    else:
        result = False
        return result 

def DataFrame(data,menu):
    if menu==2:
        df = pd.DataFrame(data, columns= ['Hostname','Type','Part','Description','Function','Serial Number'])
    elif menu==3:
        df = pd.DataFrame(data, columns= ['Hostname','Site','Memmory Used (MB)','Memmory Total (MB)','%','Status'])
    elif menu==4:
        df = pd.DataFrame(data, columns= ['Hostname','Site','CPU Utilization (%)','Status'])
    hdr = False if os.path.exists(f'./out/tmp-data.tmp') else True
    df.to_csv(f'./out/tmp-data.tmp', mode='w', header=hdr , index=False)

def ProcessExcel(nameFile):
    date_now   = datetime.now()
    time_stamp = date_now.strftime("%d-%m-%y_%H_%M")
    path ='./out/'
    file_name = nameFile +'-'+time_stamp+'.xlsx'
    file = os.path.join(path, file_name)
    new_df = pd.read_csv(f'./out/tmp-data.tmp')
    new_df.to_excel(f'{file}', index=False)
    os.remove('./out/tmp-data.tmp')