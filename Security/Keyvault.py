import datetime
import importlib as lib
import json
import sys
import time
import numpy
import pandas as pd
import requests



###################################################################################
# Make sure your tenant/ loc is correct before executing most common failure when #
####### the tenant /loc being incorrect on the parms passed to the script #######
# ##
###################################################################################
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
##################################---Parms---######################################
aas_server_list={
        'dev': 'asazure://westus2.asazure.windows.net/owfgdevaas001',
        'qa': 'asazure://canadacentral.asazure.windows.net/ofdwqadaaas002',
        'prod': 'asazure://canadacentral.asazure.windows.net/ofdwprddaaas002',
        'prod2': 'asazure://canadacentral.asazure.windows.net/ofdwprddaaas003',
        'prod3': 'asazure://canadacentral.asazure.windows.net/ofdwprddaaas004'
    }

print(sys.argv)


if len(sys.argv)        >1:
  keyvault                       = sys.argv[1]
  resource_group                 = sys.argv[2]
  subscription                   = sys.argv[3]

else :
    keyvault        ='kv-dl-prod001'
    resource_group  = 'infrastructure-rg'
    subscription    = 'e8421839-e5d6-4b95-81ae-4c0887e2589c'



class Keyvault():

    def __init__(self,keyvault,resource_group,subscription):

        self.keyvault       = keyvault
        self.resource_group = resource_group
        self.subscription   = subscription


    def validate_parms(self):
         return {'keyvault'               : self.keyvault
                 }

    @property
    def auth(self) -> str:
        try:
            self.url            = f"https://login.microsoftonline.com/{tenant}/oauth2/token"
            self.client_id      = ""
            self.client_secret  = ""
            self.context        = "https%3A//vault.azure.net"
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
    def Checkkey(self) -> str:
        try:

            self.key_url            = f"https://kv-dl-prod001.vault.azure.net/secrets/ClientSecret?api-version=7.2"
              #f"https://management.azure.com/subscriptions/{self.subscription}/resourceGroups/{self.resource_group}/providers/Microsoft.KeyVault/vaults/{self.keyvault}?api-version=2019-09-01"
            self.key_payload        = '{}'
            self.key_headers        = {'Authorization': self.auth,'Content-Type': 'application/json'}
            self.key_response       = requests.request("GET", self.key_url, headers=self.key_headers, data=self.key_payload)
            self.key_json_resp      = self.key_response.json()
            self.key_value          = self.key_json_resp

        except Exception as e:
            print(" Failed to get key from vault \n exception is : ",e)
            exit(-1)
        return json.dumps(self.key_value,indent = 4 )


print(Keyvault(subscription=subscription,resource_group=resource_group,keyvault=keyvault).Checkkey)

