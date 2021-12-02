import json
import sys
import pandas as pd
import requests
import urllib
import time


sys.path.insert(1,'C:/Users/DIS/PycharmProjects/AzureAutomation/AAS_MANAGER')

###################################################################################
# Make sure your tenant/ loc is correct before executing most common failure when #
####### the tenant /loc being incorrect on the parms passed to the script #######
# ##
###################################################################################
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
##################################---Parms---######################################

print(sys.argv)

if len(sys.argv)        >1:
  tenant                = sys.argv[1]
  storage_account       = sys.argv[2]
  file_system           = sys.argv[3]
  tgt_storage_account   = sys.argv[4]
  folders               = sys.argv[5]
  clientid              = sys.argv[6]
  clientsecret          = sys.argv[7]
  usr                   = "dis@saveonfoods.com"
  pwd                   = open('C:/Users/DIS/Python_Automation/KyGen/disKys.txt').readline()


else :
    tenant              = ''
    storage_account     = ''
    file_system         = ['test1','test2','test3','test4']
    tgt_storage_account = ''
    folders             = ['internal','general','confidential']
    clientid            = ''
    clientsecret        = ''
    usr                 = ""
    pwd                 = ""#open('C:/Users/DIS/Python_Automation/KyGen/disKys.txt').readline()



###########################################################################################

class ADLS_MANAGER():

    def __init__(self,usr,pwd,tenant,storage_account,file_system=None,tgt_storage_account=None,folders = None):

        self.tenant              = tenant
        self.storage_account     = storage_account
        self.tgt_storage_account = tgt_storage_account
        self.file_system         = file_system
        self.folders             = folders
        self.clientid            = clientid
        self.clientsecret        = clientsecret

    def validate_parms(self):
         return {'tenant'                 : self.self.tenant,
                 'storage_account'        : self.storage_account,
                 'target_storage_account' : self.tgt_storage_account,
                 'file_system'            : self.file_system,
                 'folders'                : self.folders
                 }
    @property
    def auth(self) -> str:
        try:
            self.tenant         = self.tenant
            self.url            = f"https://login.microsoftonline.com/{self.tenant}/oauth2/token"
            self.context        = "https%3A//storage.azure.com"
            self.payload        = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}&resource={self.context}'
            self.headers        = {'Content-Type': 'application/x-www-form-urlencoded','Cookie': 'stsservicecookie=ests; fpc=AnZ_VedXpZxDu1S5_EloEcH6M5VHBAAAAFsj19YOAAAA; x-ms-gateway-slice=estsfd'}
            self.response       = requests.request("POST", self.url, headers=self.headers, data=self.payload)
            self.json_resp      = self.response.json()
            self.token          = self.json_resp['access_token']
            self.token_type     = self.json_resp['token_type']
            self.bearer_token   =self.token_type.translate({ord('"'): None}) +" "+self.token.translate({ord('"'): None})

        except Exception as e:
            print("authentication failed \n exception is : ",e)
        return self.bearer_token

    @property
    def ADLS_READ_FILES_SYS(self) -> pd.DataFrame:
        if self.file_system ==None:
            try:

                self.fs_url            = f"https://{self.storage_account}.dfs.core.windows.net/?resource=account"
                self.fs_payload        = {}
                self.fs_headers        = {'Authorization': self.auth,'Content-Type': 'application/json'}
                self.fs_response       = requests.request("GET", self.fs_url, headers=self.fs_headers, data=self.fs_payload)
                self.fs_json_resp      = self.fs_response.json()
                self.fs_filesystems    = pd.read_json(json.dumps(self.fs_json_resp['filesystems']))['name']
                #self.operation_id      = self.refresh_json_resp['operationId']

            except Exception as e:
                print(" Failed to retrieve files_system \n exception is : ",e)
                print(json.dumps(self.fs_json_resp, indent=4))
                exit(-1)
            return self.fs_filesystems
        else:
            return pd.DataFrame({'name':self.file_system})['name']

    @property
    def ADLS_READ_FOLDERS(self) -> pd.DataFrame:
    # if you want to specify folders manualy instead of copying from another storage account pass this parm#
        if self.folders==None:

            ## Find all folders in Container ##
            dflist = []
            for fs in self.ADLS_READ_FILES_SYS:
                self.clonefromurl = f"https://{self.storage_account}.dfs.core.windows.net/" + fs + "?recursive=True&resource=filesystem"
                self.clonefrompayload = {}
                self.clonefromheaders = {'Authorization': self.auth, 'Content-Type': 'application/json'}
                self.clonefromresponse = requests.request("GET", self.clonefromurl, headers=self.clonefromheaders, data=self.clonefrompayload)
                self.clonefrompath = json.dumps(self.clonefromresponse.json()['paths'])
                df = pd.read_json(self.clonefrompath)
                df['files_system'] = fs
                if 'isDirectory' in df.columns:
                    filter1 = df['isDirectory'] == 'true'
                    df = df[filter1]
                    dflist.append(df)
                else:
                    next
            final_df = pd.concat(dflist)
            filesystems_out = final_df['files_system'].unique()

            return filesystems_out
        else:
            return self.folders

    @property
    def ADLS_WRITE_FS(self): # Create ADLS Containers
        try:
            for fs in self.ADLS_READ_FILES_SYS:
                    #filter1   =  self.ADLS_READ_FILES_SYS['files_system'] == fs
                    #path      =  self.ADLS_READ_FILES_SYS[filter1]
                    #pathlist  = path['name']

                    self.clonetofsurl      = f"https://{self.tgt_storage_account}.dfs.core.windows.net/"+fs+"?resource=filesystem"
                    self.clonetofspayload  = {}
                    self.clonetofsheaders  = {'Authorization': self.auth, 'Content-Type': 'application/json'}
                    self.clonetofsresponse = requests.request("PUT", self.clonetofsurl, headers=self.clonetofsheaders, data=self.clonetofspayload)
                    time.sleep(10)
                    print(self.clonetofsresponse.status_code)

        except Exception as e:
         #   print("Exception Raised:", e)
            next

    @property
    def ADLS_WRITE_FOLDER(self):  # Create Folders in Containers
            try:
                for fs in self.ADLS_READ_FILES_SYS:
                    for path in self.ADLS_READ_FOLDERS:
                        payload = {}
                        pathurl = f"https://{self.tgt_storage_account}.dfs.core.windows.net/" + fs + "/" + urllib.parse.quote_plus(path) + "?resource=directory"
                        headers = {'Authorization': self.auth, 'Content-Type': 'application/json'}
                        responsepth = requests.request("PUT", pathurl, headers=headers, data=payload)
                        print(pathurl)
                        print(path)
                        print(responsepth.content)

                return json.dumps(responsepth.json(),indent = 4)

            except Exception as e:
                #print("Exception Raised:", e)
                next



## create the file system ##
print(ADLS_MANAGER(usr=usr,pwd=pwd,tenant=tenant,storage_account=storage_account,tgt_storage_account=tgt_storage_account,file_system=file_system,folders=folders).ADLS_WRITE_FS)
## use the newly created filesystem and add folders ##
print(ADLS_MANAGER(usr=usr,pwd=pwd,tenant=tenant,storage_account=storage_account,tgt_storage_account=tgt_storage_account,file_system=file_system,folders=folders).ADLS_WRITE_FOLDER)
