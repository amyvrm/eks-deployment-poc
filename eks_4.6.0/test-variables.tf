### Test Pipeline Variables
variable "aws_region" {}

variable "cluster-name" {}

variable "key_name" {}

variable "aws_security_group" {
  default = "dev-terraform-security_group"
}

variable "terraform-iam-role-cluster" {
  default = "dev-terraform-eks"
}

variable "terraform-iam-ec2" {
  default = "dev-terraform-ec2"
}

variable "terraform-vpc" {
  default = "dev-terraform-eks-vpc"
}

variable "terraform-gateway" {
  default = "dev-terraform-eks-gateway"
}

variable "terraform-cloudtrail" {
  default = "dev-terraform-cloudtrail"
}

variable "s3-bucket" {
  default = "test-dev-eks-1"
}

variable "s3-prefix" {
  default = "cloudtrail"
}

variable "terraform-ecr-log" {
  default = "dev-terraform-ecr-log"
}