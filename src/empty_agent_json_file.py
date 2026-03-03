import requests
import json
import argparse

def upload_empty_agent_file(agent_url, nexus_usr, nexus_pwd):
    print("Removing Agent File")
    res = requests.delete(agent_url, auth=(nexus_usr, nexus_pwd))
    if res.status_code == 204:
        print("{} file has been removed".format(agent_url))
        print("Adding Empty Agent File")
        res = requests.put(agent_url, data=json.dumps([]), auth=(nexus_usr, nexus_pwd))
        if res.status_code == 201:
            print("Added {} Agent file".format(agent_url))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Please give argument for Reco scan')
    parser.add_argument("--nexus_url", action="store", help="IP address of DSM")
    parser.add_argument("--nexus_cred", nargs="+", help="User Credentials")
    args = parser.parse_args()

    nexus_usr, nexus_pwd = args.nexus_cred
    upload_empty_agent_file(args.nexus_url, nexus_usr, nexus_pwd)
