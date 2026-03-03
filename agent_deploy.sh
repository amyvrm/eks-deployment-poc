#!/bin/bash

agent_file="$10"
comp_grp="$7"
echo "Computer Group: $comp_grp"
echo "Agent File: $agent_file"

aws ec2 describe-instances --region $6 --query "Reservations[*].Instances[*].{PublicIP:PublicIpAddress,SecurityGroups:SecurityGroups[*],Name:Tags[?Key=='Name']|[0].Value,Status:State.Name,hostname:PrivateDnsName}" --filters "Name=instance-state-name,Values=running" "Name=tag:Name,Values='*$5*'" > ec2.json
python3 src/agent.py --iac_path $1 --nexus_url $2 --nexus_cred $3 $4  --region $6 --comp_grp $comp_grp --c1ws_host $8 --c1ws_key $9 --agent_file $agent_file
#aws ec2 revoke-security-group-ingress --group-id sg-0b31353020edb5059 --region us-west-2 --ip-permissions "[{\"IpProtocol\": \"tcp\", \"FromPort\": 22, \"ToPort\": 22, \"IpRanges\": [{\"CidrIp\": \"52.52.210.196/32\"}]}]"

#helm upgrade trendmicro --namespace trendmicro-system --create-namespace --values overrides.yaml https://github.com/trendmicro/cloudone-container-security-helm/archive/master.tar.gz