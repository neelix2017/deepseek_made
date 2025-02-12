def start():
    requests.post("http://192.168.0.111:8080/json.htm?type=command&param=switchlight&idx=55&switchcmd=Set%20Level&level=10")