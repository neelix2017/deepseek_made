import subprocess
import re

def start():
    temps = ''
    data = requests.get("https://meteo.arso.gov.si/uploads/probase/www/fproduct/text/sl/fcast_si_text.html").text
    mp3 = "https://meteo.arso.gov.si/uploads/probase/www/fproduct/media/sl/fcast_si_audio_hbr.mp3"
    prog = "c:/Program Files/VideoLAN/VLC/vlc"
    guid = "8fb5c852-5c8e-442d-9411-6fac2a1fb498"
    #     guid = "8fb5c852-5c8e-442d-9411-6fac2a1fb498" --> SPEAKER
    #     guid = "3504486b-d61a-400a-973e-dd47d1b78526"
    vol = 10
    #prog = f"{prog} -I null --play-and-exit --no-loop --no-repeat --aout=directsound --directx-audio-device={guid} --gain={vol} {mp3}"

    data=data.replace("\n"," ")
    result = re.search('<h2>NAPOVED ZA SLOVENIJO</h2>(.+)<h2>OBETI</h2>', data)

    data = result.group(1).replace("<p>"," ").replace("</p>"," ").replace(","," ").replace("Â°","°").replace("Å¾","z").replace("Ä","c").replace("Å¡","s")
    print(data)

    subprocess.Popen([prog,   mp3 , "-I null", "--play-and-exit", "--no-loop","--aout=directsound","--directx-audio-device="+guid])

    requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.dialog.scroller", "params": {"image": "http://192.168.0.111:8080/images/temperature.png", "line": data, "time": "30"}}})
