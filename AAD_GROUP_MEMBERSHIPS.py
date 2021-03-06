 ####################################################################################################################
##### This script requires that you have run the AAD users script first as it is used as an input to this script   #####
##### this script uses asyncio to process the rest requests concurrently due to large size of AAD users list       #####
##### Choose to pull the groups for each user instead of users in a group since nested groups in a group are messy #####
 ####################################################################################################################
 
 
import requests,sys,json,os,datetime as dt ,time, pandas as pd, importlib as lib
import asyncio
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor
import GRAPH_BEARER_TOKEN as abt
################pandas settings ##################
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
##################################################
###################Variables######################
run_var = 0
tmp= []
START_TIME = default_timer()
query_date_start = str(dt.datetime.now().date() - dt.timedelta(run_var+1)).replace('-',"")
query_date_end = str(dt.datetime.now().date() - dt.timedelta(run_var)).replace('-',"")
input_path = 'Python_Export/Azure/AAD/USERS/users_'+query_date_start+'_'+query_date_end+'.parquet'
output_path = 'Python_Export/Azure/AAD/MEMBERSHIPS/members_'+query_date_start+'_'+query_date_end+'.parquet'
pyld = '{"securityEnabledOnly": "false"}'
jsonpayload = json.loads(pyld)
textpayload = json.dumps(jsonpayload)

###################################################
#################### functions ####################
def fetch(session, id):
    base_url = "https://graph.microsoft.com/v1.0/users/"
    with session:
        lib.reload(abt) ##if your process exceed bearer token expiry can cause failure this will reload bearer token on every run##
        headers = {
        'Authorization': abt.token,
        'Content-Type': 'application/json'
         }
        full_url = base_url + id + '/getMemberGroups'
        response = requests.request("POST", full_url, headers=headers, data=textpayload)
        data = response.json()
        if response.status_code != 200:
            print("FAILURE::{0}".format(base_url + id + '/getMemberGroups'))
            exit(-1)
        elapsed = default_timer() - START_TIME
        time_completed_at = "{:5.2f}s".format(elapsed)
        print("{0:<30} {1:>20}".format(id, time_completed_at))
        if 'value' in data.keys() and len(data) >= 1:
            af = pd.DataFrame(data=data['value'], columns=['GROUP_ID'])
            af['GROUP_MEMBERS_ID'] = id
            tmp.append(af)
        return tmp

async def get_data_asynchronous():
    read_groups = pd.read_parquet(input_path)
    df = read_groups
    id_to_fetch = df['id']
    print("{0:<30} {1:>20}".format("File", "Completed at"))
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, id) # Allows us to pass in multiple arguments to `fetch`
                )
                for id in id_to_fetch
            ]
            for response in await asyncio.gather(*tasks):
                pass
def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)
############################################################
main()
df = pd.concat(tmp)
df.reset_index(drop=True, inplace=True)
df['Processed_By'] = 'DIS'
df['Processed_Date'] = dt.date.today()
df['Processed_Time'] = dt.datetime.now().timetz()
df['Active_Record'] = 1
print(df)
df.to_parquet(output_path)

