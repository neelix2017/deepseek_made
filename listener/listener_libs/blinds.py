#requests.post("http://192.168.0.111:8080/json.htm?type=command&param=switchscene&idx=3&switchcmd=Off&level=0

def start():
    data = json.loads(requests.post("http://192.168.0.111:8080/json.htm?type=command&param=getscenes").text)
    for device in data['result']:
        if ('Rolete' in device['Name']):
        
            print(device['Name'], device['Status'])
            if (device['Status']=='Off'):
                requests.post("http://192.168.0.111:8080/json.htm?type=command&param=switchscene&idx=1&switchcmd=On")
            elif (device['Status']=='On'):
                requests.post("http://192.168.0.111:8080/json.htm?type=command&param=switchscene&idx=1&switchcmd=Off")