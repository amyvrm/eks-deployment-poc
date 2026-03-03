# EKS Deployment POC

## Overview
This repository contains infrastructure as code for deploying an EKS (Elastic Kubernetes Service) cluster on AWS with automated deployment pipelines.

## Features
- Terraform configuration for EKS cluster setup
- Automated agent deployment scripts
- Kubernetes manifests for application deployment
- Security integration capabilities

## Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 0.12
- kubectl
- Python 3.x

## Project Structure
```
.
├── eks_4.6.0/          # Terraform configurations for EKS
├── deploy_agent/       # Agent deployment scripts
├── k8s/                # Kubernetes manifests
├── src/                # Python scripts for automation
└── README.md
```

## Usage

### Deploy EKS Cluster
1. Navigate to the `eks_4.6.0/` directory
2. Update `variables.tf` with your configuration
3. Run:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

### Deploy Agent
1. Update configuration in `deploy_agent/variables.tf`
2. Run the deployment script:
   ```bash
   ./agent_deploy.sh
   ```

### Clean Up
To destroy the infrastructure:
```bash
./destroy.sh
```

## Security Notes
- Never commit sensitive files (`.pem`, `.key`, credentials)
- Use environment variables or AWS Secrets Manager for sensitive data
- Review `.gitignore` before committing changes

## License
MIT