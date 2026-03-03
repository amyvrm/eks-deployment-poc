#!/usr/bin/env python3

import argparse
import shutil, os
import subprocess
import json
import requests
import configparser
from agent_operation import CompGroup


class EksAgent:
    def __init__(self, iac_path, nexus_url, nexus_cred, conf_file, query_file, region, key_name,
                 comp_grp, c1ws_host, c1ws_key, agent_file):
        api_version = "v1"
        self.iac_path = iac_path
        self.region = region
        self.key_name = key_name

        comp = CompGroup(c1ws_host, c1ws_key, api_version)
        self.comp_grp_id = comp.get_comp_grp(comp_grp)

        self.agent_file = agent_file
        dst = os.getcwd()
        self.pem_file_path = os.path.join(dst, self.iac_path)

        self.agents = self.get_agent_file(nexus_url, nexus_cred)
        self.queries = self.get_query_file(query_file)
        self.policy_id = self.get_policy_id(conf_file)

    def get_agent_file(self, nexus_url, nexus_cred):
        res = requests.get(nexus_url, auth=nexus_cred)
        print("{} Get status code: {}".format(nexus_url, res.status_code))
        if res.status_code == 404:
            print("# {} Not Found, creating empty file".format(nexus_url))
            response = json.dumps([])
            res = requests.put(nexus_url, data=response, auth=nexus_cred)
            print("{} Put status code: {}".format(nexus_url, res.status_code))
            return json.loads(response)
        elif res.status_code == 200:
            response = res.json()
            return response
        else:
            raise Exception("Status code 404 and 200 not found")

    def set_agent_file(self, hostname, status):
        print("Set -> hostname: {} status: {}".format(hostname, status))
        set_agent = True
        for agent_entry in self.agents:
            if hostname == agent_entry["hostname"]:
                agent_entry["agent"] = status
                set_agent = False
        if set_agent:
            self.agents.append({"hostname": hostname, "status": status})
        with open(self.agent_file, "w") as fin:
            json.dump(self.agents, fin, indent=4)

    def get_query_file(self, query_file):
        with open(query_file) as fout:
            return json.load(fout)

    def get_policy_id(self, conf_file):
        config = configparser.ConfigParser()
        config.read(conf_file)
        return config['POLICY']['ID']

    def parse_agent_file(self):
        for node_info in self.queries:
            for node_data in node_info:
                ip = node_data["PublicIP"]
                sgid = node_data["SecurityGroups"][0]["GroupId"]
                hostname = node_data["hostname"]
                print("# Hostname {} found in eks".format(hostname))
                if self.check_host_entry(hostname):
                    self.terraform_initialize()
                    self.terrform_apply(ip, sgid)
                    self.set_agent_file(hostname, "installed")
                    print("Agent has been added, now removing the ssh ip")
                    self.terrform_remove_rule(sgid)
                    self.install_c1cs()

    def check_host_entry(self, hostname):
        print("Agest List Entries: {}".format(self.agents))
        for agent_entry in self.agents:
            if hostname == agent_entry["hostname"]:
                print("Checking {} in Agent List".format(hostname))
                if agent_entry["status"] != "installed":
                    return True
                else:
                    print("# {} has already deployed agent. {}".format(hostname, agent_entry))
                    return False
        print("{} Entry is not found in Agent List".format(hostname))
        return True


    def terraform_initialize(self):
        # cmd = ["terraform", "-chdir={}".format(self.iac_path), "init", "-upgrade"]
        cmd = ["terraform", "-chdir={}".format(self.iac_path), "init"]
        self.execute_terraform_cmd(cmd)

    def terrform_apply(self, ip, sgid):
        cmd = ["terraform", "-chdir={}".format(self.iac_path), "apply",
               "-var", "aws_region={}".format(self.region),
               "-var", "key_name={}".format(self.key_name),
               "-var", "ip={}".format(ip),
               "-var", "path={}".format(self.pem_file_path),
               "-var", "policy_id={}".format(self.policy_id),
               "-var", "comp_grp={}".format(self.comp_grp_id),
               "-var", "sgid={}".format(sgid), "-auto-approve"
               ]
        self.execute_terraform_cmd(cmd)

    def terrform_remove_rule(self, sgid):
        ip_range_wo = self.terraform_get_ip()
        ip_range = ip_range_wo.replace('"', "")
        print("# Removing {} rule from security group {}".format(ip_range, sgid))
        ip_protocol = [{
                            "IpProtocol": "tcp",
                            "FromPort": 22,
                            "ToPort": 22,
                            "IpRanges": [{"CidrIp": ip_range}]
                        }]

        cmd = ["aws", "ec2", "revoke-security-group-ingress", "--group-id", sgid, "--region", self.region,
               "--ip-permissions", json.dumps(ip_protocol)]
        self.execute_terraform_cmd(cmd)

    def install_c1cs(self):
        print("# Installing C1CS in Node...")
        cmd = ["helm", "install", "trendmicro", "--namespace", "kube-system",
               "--create-namespace", "--values", "overrides.yaml",
               "https://github.com/trendmicro/cloudone-container-security-helm/archive/master.tar.gz"]
        self.execute_terraform_cmd(cmd)

    def execute_terraform_cmd(self, cmd):
        cmd_ret = subprocess.call(cmd)
        if cmd_ret != 0:
            print("Exception! in terraform command {}".format(cmd))

    def terraform_get_ip(self):
        cmd = ["terraform", "-chdir={}".format(self.iac_path), "output", "sgip"]
        cmd_ret = subprocess.run(cmd, stdout=subprocess.PIPE)
        return cmd_ret.stdout.decode('utf-8').strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Please give argument to perform Agent operations')
    parser.add_argument("--iac_path", action="store", help="IAC source code")
    parser.add_argument("--nexus_url", action="store", help="IP address of DSM")
    parser.add_argument("--nexus_cred", nargs="+", help="User Credentials")
    parser.add_argument("--region", action="store", help="region of aws cloud")
    parser.add_argument("--key_name", action="store", help="ssh key")
    parser.add_argument("--comp_grp", action="store", help="computer group name")
    parser.add_argument("--c1ws_host", action="store", help="c1ws host url")
    parser.add_argument("--c1ws_key", action="store", help="c1ws key")
    parser.add_argument("--agent_file", action="store", help="Agent file")
    args = parser.parse_args()

    conf_file = 'k8s/config.ini'
    query_file = "ec2.json"
    nexus_usr, nexus_pwd = args.nexus_cred
    nexus_cred = (nexus_usr, nexus_pwd)

    node = EksAgent(args.iac_path, args.nexus_url, nexus_cred, conf_file, query_file, args.region, args.key_name,
                    args.comp_grp, args.c1ws_host, args.c1ws_key, args.agent_file)
    node.parse_agent_file()
