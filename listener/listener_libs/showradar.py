def start():
    requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.hello.world", "params": {"image": "https://meteo.arso.gov.si/uploads/probase/www/observ/radar/si0_zm_si_small_latest.jpg", "line1": "    _    ","rate":"5","box":"1000 74 240 180","ask":"0"}}} )
               
