import requests,sys,json,os,datetime as dt ,time, pandas as pd
from GRAPH_BEARER_TOKEN import clientid,bearertoken,pickytoken

###################################################################################
# Make sure your tenant/ loc is correct before executing most common failure when #
####### the tenant /loc being incorrect on the parms passed to the script #########
# i choose to output as a parquet but feel free to change pandas output as needed #
#    pull from the users object or the groups object specify on the table parm    #
###################################################################################

##################################---Parms---######################################
print(sys.argv)
if len(sys.argv)>1:
  table = sys.argv[1]
else:
    table = 'users' # if you don't want to run by passing parms #
userarray = []
page = 0
i = 0
run_var = 0
path = ''
query_date_start = str(dt.datetime.now().date() - dt.timedelta(run_var)).replace('-',"")
query_date_end = str(dt.datetime.now().date() - dt.timedelta(run_var-1)).replace('-',"")
output_path = path+table.upper()+'/'+table+'_'+query_date_start+'_'+query_date_end+'.parquet'
#############################  make request #######################################


url = 'https://graph.microsoft.com/v1.0/'+table
      #users'#groups
pyld = '{}'
jsonpayload = json.loads(pyld)
textpayload = json.dumps(jsonpayload)
headers = {
  'Authorization': pickytoken,
  'Content-Type': 'application/json'
}
response = requests.request("GET", url, headers=headers, data=textpayload)
################################ extract values ########################################

response_text = json.loads(response.text.encode('utf8'))
next_page = response_text['@odata.nextLink']
raw_data = response.json()
raw_value = raw_data['value']
while i <= len(raw_value)-1:
  userarray.append(raw_value[i])
  i += 1
try:
    while '@odata.nextLink' in response_text.keys() and len(json.dumps(response_text['@odata.nextLink']))>2:
        response_text = json.loads(response.text.encode('utf8'))
        next_page = response_text['@odata.nextLink']
        response = requests.request("GET", next_page, headers=headers, data=textpayload)
        raw_data = response.json()
        raw_value = raw_data['value']
        i = 0
        while i <= len(raw_value) - 1:
          userarray.append(raw_value[i])
          i += 1
        page += 1

except: next
df = pd.DataFrame(userarray)
df['Processed_By'] = 'DIS'
df['Processed_Date'] = dt.date.today()
df['Processed_Time'] = dt.datetime.now().timetz()
print(userarray)
df.to_parquet(output_path)
