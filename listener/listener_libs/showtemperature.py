def start():
    temps = ''
    data = json.loads(requests.post("http://192.168.0.111:8080/json.htm?type=command&param=getdevices&filter=temp&used=true&order=Name").text)
    for device in data['result']:
        if ('Temp + Humidity' in device['Type']): 
            datetime_object = datetime.strptime(device['LastUpdate'], '%Y-%m-%d %H:%M:%S')
            if((datetime.now()-datetime_object)<timedelta(hours=1)):
                temps = (f"     {device['Name']}  ( {device['Temp']}°C, {device['Humidity']}% )    ") + temps
    requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.dialog.scroller", "params": {"image": "http://192.168.0.111:8080/images/temperature.png", "line": temps, "time": "30"}}})
