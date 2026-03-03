#### Production Pipeline Variables

variable "aws_region" {}

variable "cluster-name" {}

variable "key_name" {}

variable "aws_security_group" {
  default = "terraform-security_group"
}

variable "terraform-iam-role-cluster" {
  default = "terraform-eks"
}

variable "terraform-iam-ec2" {
  default = "terraform-ec2"
}

variable "terraform-vpc" {
  default = "terraform-eks-vpc"
}

variable "terraform-gateway" {
  default = "terraform-eks-gateway"
}

variable "terraform-cloudtrail" {
  default = "terraform-cloudtrail"
}

variable "s3-bucket" {
  default = "dev-eks-1"
}

variable "s3-prefix" {
  default = "cloudtrail"
}

variable "terraform-ecr-log" {
  default = "terraform-ecr-log"
}
