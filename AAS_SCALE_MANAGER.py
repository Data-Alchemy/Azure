###################################################################################
##This script is used as a shell to scale up or down a specific AAS server this ###
## will allow a reduction in cost for the organization while increasing delivery.##
## This script is to be called by a automation service that passes parms for exc ##
###################################################################################


import requests,sys,json,os,datetime,time
sys.path.insert(1,'C:/Users/DIS/PycharmProjects/AzureAutomation/AAS_CNTRL')
from BEARER_TOKEN import clientid,bearertoken,pickytoken

###################################################################################
# Make sure your tenant/ loc is correct before executing most common failure when #
####### the tenant /loc being incorrect on the parms passed to the script #########
###################################################################################


########################################
######Parms Passed To Application#######

####################Avail Tenants####################
ProdTenant = {}
DevTenant = {}
#####################################################
cmdexec = sys.argv[1] #SKU to Scale
server = sys.argv[2] #'ofdwprddaaas002'#'ofdwqadaaas002' #
rg = sys.argv[3] #'RG-dna-prod'#'RG-dna-qa' #'RG-dna-sandbox' #sys.argv[3]
location = sys.argv[4] #'Canada Central'
tnt = sys.argv[5]

if tnt == 'Prod':
    tenant = ProdTenant
    print(tenant)
elif tnt == 'Dev':
    tenant =DevTenant

else: print('Invalid Tenant submitted must be Prod or Dev') and exit
'''  
#enable for parm validation if needed#
print('CMD=', cmdexec)
print('Server =',server)
print('Resource =',rg)
print('Loc=',location)
print('tenant=',tnt)
'''

########################################
######Log processing variables##########
sessionstart = str(datetime.datetime.now())
fnsession = str(datetime.date.today())
target = "" # enter path to output log files
log = "AAS_SCALE_LOG_"+ fnsession +".txt"
run_log= open(os.path.join(target,log),"a+")

message1 = "user session initiated "
message2 = "autenticated by " + clientid
message3 = "****************" 
message4 = "Command initiated SKU changed to -------------->" + cmdexec
message5 = "Session Terminated "
########################################

########################################
#########Execution Script###############

url = "https://management.azure.com/subscriptions/"+tenant+"/resourceGroups/"+rg+"/providers/Microsoft.AnalysisServices/servers/"+server+"?api-version=2017-08-01"
pyld = '{"sku": {"capacity": 1,"name": "'+cmdexec+'","tier": "Standard"}}'

if cmdexec not in ['S1', 'S2', 'S4']:
  print(sessionstart+' '+message1+ '\n' +' '+ message2+ '\n'+' endpoint used '+url+ '\n' + ' Error SKU parms passed are not valid must be S1, S2 or S4 not' +' '+cmdexec  + '\n' + message5, file=run_log)
  exit()

jsonpayload = json.loads(pyld)
textpayload = json.dumps(jsonpayload)
headers = {
#'content-security-policy':  'self',
  'Authorization': pickytoken,
  'Content-Type': 'application/json'
}
response = requests.request("PATCH", url, headers=headers, data=textpayload)
#payload)
print(response.text.encode('utf8'))
#####################GEN LOG FILES############################
if cmdexec not in ['S1', 'S2', 'S4']:
  print(message1 + '\n' + 'Error parms passed are not valid ' + cmdexec + '\n' + message2 + '\n' + message5, file=run_log)
  exit()
else:
  print(message1 + str(response.text.encode('utf8')) +'\n' +message2 + '\n' +message3 + '\n' + message4 + '\n' + message5 + str(datetime.datetime.now()),file=run_log)
  time.sleep(80)
  print('execution complete')
  exit()
##############################################################
