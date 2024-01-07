import win32com.client
import psutil
import requests
import base64
import json
import webbrowser

__author__ = "@MA-M0ustache"

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class ClientData:
    def __init__(self):
        self.isRunning = False
        self.ProcessId = 0
        self.cmdline = ""
        self.RiotPort = 0
        self.RiotToken = ""
        self.ClientPort = 0
        self.ClientToken = ""
        
def extract_content(str_source, str_start, str_end):
    if str_start in str_source and str_end in str_source:
        start = str_source.index(str_start) + len(str_start)
        end = str_source.index(str_end, start)
        return str_source[start:end]
    return ""


def make_request(info, method, url, client):
    port = info.ClientPort if client else info.RiotPort
    auth_token = info.ClientToken if client else info.RiotToken

    try:
        headers = {'Authorization': f'Basic {auth_token}', 'Content-Type': 'application/json'}
        response = requests.request(method, f'https://127.0.0.1:{port}{url}', headers=headers, verify=False)
        return response.text
    except:
        return ''
        
    
ClientInfo = ClientData()

processes = [process for process in psutil.process_iter() if process.name() == "LeagueClientUx.exe"]

if len(processes) > 0:
    ClientInfo.isRunning = True
    ClientInfo.ProcessId = processes[0].pid
    if ClientInfo.cmdline == "":
        for process in processes:
            if process.name() == "LeagueClientUx.exe":
                
                ClientInfo.cmdline = process.name() + " [" + ','.join(process.cmdline()) + "]"
                ClientInfo.RiotPort = int(extract_content(ClientInfo.cmdline, "--riotclient-app-port=", "," "--no-rads"))
                ClientInfo.RiotToken = str(base64.b64encode((b"riot:" + extract_content(ClientInfo.cmdline, "--riotclient-auth-token=", "," "--riotclient").encode("ISO-8859-1"))), "utf-8")
                ClientInfo.ClientPort = int(extract_content(ClientInfo.cmdline, "--app-port=", "," "--install"))
                ClientInfo.ClientToken = str(base64.b64encode((b"riot:" + extract_content(ClientInfo.cmdline, "--remoting-auth-token=", "," "--respawn-command=LeagueClient.exe").encode("ISO-8859-1"))), "utf-8")
                
                participants = []

                data_set = json.loads(make_request(ClientInfo, "GET", "/chat/v5/participants/champ-select", client=False))
                data_table = data_set.get("participants")
                if len(data_table) == 5:
                    for row in data_table:
                        participants.append(row.get("game_name")+"%23"+row.get("game_tag"))
                    url = "https://www.op.gg/multisearch/euw?summoners=" + ",".join(participants)
                    webbrowser.open_new_tab(url)