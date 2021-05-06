import requests
import json
clientid= {}
clientsecret ={}
tenant = {}
url = "https://login.microsoftonline.com/"+tenant+"/oauth2/v2.0/token"
payload = 'grant_type=client_credentials&client_id='+clientid+'&client_secret='+clientsecret+'&scope=esource=https%3A//*.asazure.windows.net'
headers = {
   'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data = payload)
data = response.json()
bearertoken = data['access_token']
tokentype = json.dumps((data['token_type']))
pickytoken = tokentype.translate({ord('"'): None}) +" "+bearertoken.translate({ord('"'): None})
