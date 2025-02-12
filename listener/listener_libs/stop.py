def start():
    requests.post("http://192.168.0.111:9091/jsonrpc", json = {"jsonrpc":"2.0","id":1,"method":"Player.Stop","params":{"playerid": 0}})

    requests.post("http://192.168.0.111:9091/jsonrpc", json = {"jsonrpc":"2.0","id":1,"method":"Player.Stop","params":{"playerid": 1}})

    try:
        os.system('"taskkill /f /im vlc.exe')
    finally:
        print('stop')