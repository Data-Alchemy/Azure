import requests,sys,json,os,datetime,time,importlib as lib, pandas as pd
import ASA_BEARER_TOKEN as abt

###################################################################################
# Make sure your tenant/ loc is correct before executing most common failure when #
####### the tenant /loc being incorrect on the parms passed to the script #########
###################################################################################
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
##################################---Parms---######################################
print(sys.argv)
if len(sys.argv)>1:
  model = sys.argv[1]
  server = sys.argv[2]
  location = sys.argv[3]
  poll_interval = int(sys.argv[4])
else :
    model = 'CrawlPhaseSemanticModel'
    server = 'ofdwprddaaas002'
    location = 'canadacentral'
    poll_interval = 60


print("parms received:",'\nModel:',model,'\nServer:',server,'\nlocation:',location)
############################# start refresh #######################################
url = "https://"+location+".asazure.windows.net/servers/"+server+"/models/"+model+"/refreshes"
pyld = '{"Type": "Full","CommitMode": "partialBatch","MaxParallelism": 10,"RetryCount": 2}' # if no objects are passed a full reload of the model is done#

jsonpayload = json.loads(pyld)
textpayload = json.dumps(jsonpayload)
headers = {
  'Authorization': abt.pickytoken,
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=textpayload)
response_details = json.loads(response.content)
###### Check to see if there is a job currently running ######
###### monitor existing run instead of creating new one ######
if 'code' in response_details.keys():
    print(response_details['message'],'\n job id :'+response_details['details'][0]['message'])
    operation_id = response_details['details'][0]['message']
    #print('1')
    exit(-1)
##############################################################
######### if no refresh is running start a new run ###########
else:
    #print(response_details)
    #print('2')
    operation_id = response_details['operationId']
    print("\nRefresh intialized with response id:",
    response_details['operationId'] + '\n start time : ' + str(datetime.datetime.today()))
    time.sleep(10)
    #####################check status############################
    url = "https://" + location + ".asazure.windows.net/servers/" + server + "/models/" + model + "/refreshes/" + operation_id
    headers = {
        'Authorization': abt.pickytoken,
        'Content-Type': 'application/json'
    }
    pyld = {}
    response = requests.request("GET", url, headers=headers, data=pyld)
    status_details = json.loads(response.content)
    # print(status_details)
    print('\nStarting Heartbeat : ')
    print(' start time: ' + str(datetime.datetime.today()))
    if status_details['status'] == 'failed':
        print(pd.json_normalize(status_details,max_level=0)['messages'][0][0])
        #print('3')
        exit(-1)
    else:
        while status_details['status'] == 'inProgress':
            #print('4')
            try:
                lib.reload(abt) #reauthenticate so that no failure comes up when checking status
                headers = {
                    'Authorization': abt.pickytoken,
                    'Content-Type': 'application/json'
                }
                print(abt.pickytoken)
                ###### pretty sysout #######
                response = requests.request("GET", url, headers=headers, data=pyld)
                status_details = json.loads(response.content)
                obj = status_details['objects']
                status = pd.DataFrame(obj)
                print(status.groupby('status').agg('count'))
                for a in status['status']:
                    if a != 'succeeded':
                        status['processing_time'] = datetime.datetime.now().strftime("%H:%M:%S")
                    else:
                        status['processing_time'] = "Complete"
                ################################
                print('\nChecking status : ' + '\n####################')
                print(' process is currently in ' + status_details['status'] + ' status')
                #print('\n Objects processed:', status_details['objects'])
                print(status)
                print('####################')
                print(' end time: ' + str(datetime.datetime.today()))
                if status_details['status'] == 'failed':
                    print(response.json)
                    exit(-1)
                else:
                    time.sleep(poll_interval*5)
            except:
                print(status_details)
                exit(-1)

##############################################################
