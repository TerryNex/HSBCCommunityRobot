import requests

url = "https://serviceapi-command.square-community.com.au/AuthorizationService/ParticipantLogin"

payload = {
  'username': "hl928452957@gmail.com",
  'password': "ronqex-7kyxfe-mikmuQ",
  'change': "undefined"
}

headers = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
  'origin': "https://hsbccommunityhk.square-community.com.au"
}

response = requests.post(url, data=payload, headers=headers)

print(response.text)
