#!/usr/bin/python3

import argparse
import zeep
import urllib3


def delete_host(dsm_url, c1ws_cred, host_name, tenant_name):
    urllib3.disable_warnings()
    wsdl_url = "{}/webservice/Manager?WSDL".format(dsm_url)
    transport = zeep.Transport()
    transport.session.verify = False  # Bypass self-signed certificate errors
    client = zeep.Client(wsdl=wsdl_url, transport=transport)
    uname, pwd = c1ws_cred
    sID = client.service.authenticateTenant(tenantName=tenant_name, username=uname, password=pwd)
    print("Login successful")
    host = client.service.hostRetrieveByName(hostname=host_name, sID=sID)
    host_id = host.ID
    client.service.hostDelete(host_id, sID=sID)
    print("Removed Host {} successful from {}".format(host_name, dsm_url))




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", action="store", help="IP address of DSM")
    parser.add_argument("--credentials", nargs="+", help="User Credentials")
    parser.add_argument("--host_name", action="store", help="Hostname")
    parser.add_argument("--tenant", action="store", help="Tenant Name", required=True)
    args = parser.parse_args()

    with open(args.host_name) as fout:
        hostnames = fout.read().split(",")
        for hostname in hostnames:
            print("Removing host: {}".format(hostname))
            delete_host(args.ip, args.credentials, args.host_name, args.tenant)
