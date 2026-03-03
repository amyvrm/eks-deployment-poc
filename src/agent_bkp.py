import shutil, os
import subprocess
import json


def check_file_exist(file_name):
    if os.path.exists(file_name):
        return True


def create_ip_list(file_name, msg, hostname):
    ips = []
    dns_list = []
    if not check_file_exist(file_name):
        raise Exception("Error! {} file not found".format(file_name))
    with open(file_name) as fout:
        data = json.load(fout)
        for info_set in data[0]:
            info = {
                "ip": info_set[msg],
                "sg-id": info_set["SecurityGroups"][0]["GroupId"]
            }
            ips.append(info)
            dns_list.append(info_set[hostname])
        """      
        for line in fout:
        if msg in line:
          ip_with_quotes = line.split(":")[1].split(",")[0].strip()
          ip=ip_with_quotes.replace('"','') 
          ips.append(ip)
        """
    return ips, dns_list


if __name__ == '__main__':
    file_name = "ec2.json"
    ip = "PublicIP"
    hostname = "DnsName"
    iac_path = "eks_4.6.0"
    destroy_file = "main.destroy.tfplan"
    hostname_file = "hostname.txt"
    dst = os.getcwd()
    dst_path = os.path.join(dst, iac_path)
    src_path = os.path.join(dst, "src")
    src = os.path.join(src_path, "../deploy_agent/install.tf")
    print("src: {} and dst: {} path".format(src, dst_path))

    ip_list, dns_list = create_ip_list(file_name, ip, hostname)
    print(ip_list, dns_list)
    if len(ip_list) == 0:
        raise Exception("Error! credential not found")

    with open(hostname_file, "w") as fin:
        fin.write(",".join(dns_list))

    shutil.copy(src, dst_path)
    cmd_ret = subprocess.call(["terraform", "-chdir={}".format(iac_path), "init", "-upgrade"])
    if cmd_ret != 0:
        print("Failed in init upgrade")

    for data in ip_list:
        cmd_ret = subprocess.call(["terraform", "-chdir={}".format(iac_path), "apply",
                                   "-var", "ip={}".format(data["ip"]),
                                   "-var", "path={}".format(src_path),
                                   "-var", "sgid={}".format(data["sg-id"]), "-auto-approve"])
        if cmd_ret != 0:
            print("Exception ! in terraform apply")

    cmd_ret = subprocess.call(["terraform", "-chdir={}".format(iac_path), "plan",
                               "-destroy", "-out={}".format(destroy_file),
                               "-var", "ip={}".format(data["ip"]),
                               "-var", "path={}".format(src_path),
                               "-var", "sgid={}".format(data["sg-id"])])
    if cmd_ret != 0:
        print("Exception ! in terraform apply")