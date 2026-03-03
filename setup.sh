#!/bin/bash

aws configure set default.region $1
aws configure set aws_access_key_id $2
aws configure set aws_secret_access_key $3
aws configure set aws_default_output json
aws eks --region $1 update-kubeconfig --name $4
