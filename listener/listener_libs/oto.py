def start():
    requests.post("http://192.168.0.111:9091/jsonrpc", json = {"jsonrpc":"2.0","id":1,"method":"Player.Open","params":{"item":{"channelid":1907}}})