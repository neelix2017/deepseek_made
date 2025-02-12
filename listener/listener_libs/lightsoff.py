#requests.post("http://192.168.0.111:8080/json.htm?type=command&param=switchscene&idx=3&switchcmd=Off&level=0

def start():
    data = json.loads(requests.post("http://192.168.0.111:8080/json.htm?type=command&param=getdevices&filter=light&used=true&order=Name").text)
    for device in data['result']:
        if ('Light' in device['Image'] and (('light' in device['TypeImg']) or ('dimmer' in device['TypeImg']))):
            print(device['Name'], device['Status'])
            #if (device['Status']!='Off'):
            requests.post("http://192.168.0.111:8080/json.htm?type=command&param=switchlight&switchcmd=Off&idx="+device['idx'])