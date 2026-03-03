#
# EKS Cluster Resources
#  * IAM Role to allow EKS service to manage other AWS services
#  * EC2 Security Group to allow networking traffic with EKS cluster
#  * EKS Cluster
#

resource "aws_iam_role" "terraform-iam-role-cluster" {
  name = var.terraform-iam-role-cluster

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "terraform-cluster-AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.terraform-iam-role-cluster.name
}

resource "aws_iam_role_policy_attachment" "terraform-cluster-AmazonEKSVPCResourceController" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.terraform-iam-role-cluster.name
}

resource "aws_security_group" "terraform-secuirty-grp" {
  name        = var.aws_security_group
  description = "Cluster communication with worker nodes"
  vpc_id      = aws_vpc.terraform-vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.aws_security_group
  }
}


#resource "aws_security_group_rule" "demo-cluster-ingress-workstation-ssh" {
#  cidr_blocks       = [local.workstation-external-cidr]
#  description       = "Allow workstation to communicate with the cluster"
#  from_port         = 22
#  protocol          = "tcp"
#  security_group_id = aws_security_group.demo-cluster.id
#  to_port           = 22
#  type              = "ingress"
#}

resource "aws_security_group_rule" "terraform-cluster-ingress-workstation-https" {
  cidr_blocks       = [local.workstation-external-cidr]
  description       = "Allow workstation to communicate with the cluster API Server"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.terraform-secuirty-grp.id
  to_port           = 443
  type              = "ingress"
}

resource "aws_eks_cluster" "dev-eks-cluster" {
  name                      = var.cluster-name
  role_arn                  = aws_iam_role.terraform-iam-role-cluster.arn
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  vpc_config {
    security_group_ids = [aws_security_group.terraform-secuirty-grp.id]
    subnet_ids         = aws_subnet.terraform-subnet[*].id
  }

  depends_on = [
    aws_iam_role_policy_attachment.terraform-cluster-AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.terraform-cluster-AmazonEKSVPCResourceController,
  ]
}
