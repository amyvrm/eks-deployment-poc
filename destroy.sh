#!/bin/bash

iac_path=$1
for file in k8s/*.yaml;
do
    echo "Yaml file: ${file}"
    kubectl delete -f $file
done

#terraform -chdir=$iac_path init
#terraform -chdir=$iac_path init -backend=false
terraform -chdir=$iac_path apply $2