#!/bin/bash

iac_path=$5
plan="create.tfplan"

aws configure set default.region $1
aws configure set aws_access_key_id $2
aws configure set aws_secret_access_key $3
aws configure set aws_default_output json

terraform -chdir=$iac_path init
terraform -chdir=$iac_path validate
terraform -chdir=$iac_path plan -var aws_region=$1 -var cluster-name=$4 -var key_name=$7 -out $plan
terraform -chdir=$iac_path apply -auto-approve $plan

#aws ec2 describe-instances --region us-west-2 --query "Reservations[*].Instances[*].{PublicIP:PublicIpAddress,SecurityGroups:SecurityGroups[*],Name:Tags[?Key=='Name']|[0].Value,Status:State.Name}" --filters "Name=instance-state-name,Values=running" "Name=tag:Name,Values='*dev-eks-1*'" --profile terraform > ec2.txt
#aws ec2 describe-instances --region us-west-2 --query "Reservations[*].Instances[*].{PublicIP:PublicIpAddress,SecurityGroups:SecurityGroups[*],Name:Tags[?Key=='Name']|[0].Value,Status:State.Name}" --filters "Name=instance-state-name,Values=running" "Name=tag:Name,Values='*dev-eks-1*'" > ec2.json
#aws ec2 describe-instances --region $1 --query "Reservations[*].Instances[*].{PublicIP:PublicIpAddress,SecurityGroups:SecurityGroups[*],Name:Tags[?Key=='Name']|[0].Value,Status:State.Name,hostname:PrivateDnsName}" --filters "Name=instance-state-name,Values=running" "Name=tag:Name,Values='*$4*'" > ec2.json

aws eks --region $1 update-kubeconfig --name $4

for file in k8s/*.yaml;
do
    kubectl apply -f $file
    kubectl get pods
    kubectl get svc
done
kubectl get svc
echo "service will be up within 5 min"

terraform -chdir=$iac_path plan -var aws_region=$1 -var cluster-name=$4 -var key_name=$7 -destroy -out $6
