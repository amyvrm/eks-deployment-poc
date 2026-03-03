#
# EKS Worker Nodes Resources
#  * IAM role allowing Kubernetes actions to access other AWS services
#  * EKS Node Group to launch worker nodes
#

resource "aws_iam_role" "terraform-iam-ec2" {
  name = var.terraform-iam-ec2

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "terraform-node-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.terraform-iam-ec2.name
}

resource "aws_iam_role_policy_attachment" "terraform-node-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.terraform-iam-ec2.name
}

resource "aws_iam_role_policy_attachment" "terraform-node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.terraform-iam-ec2.name
}

resource "aws_eks_node_group" "dev-eks-node" {
  cluster_name    = aws_eks_cluster.dev-eks-cluster.name
  node_group_name = "node-test-grp"
  node_role_arn   = aws_iam_role.terraform-iam-ec2.arn
  subnet_ids      = aws_subnet.terraform-subnet[*].id
  #subnet_ids = [aws_subnet.demo[*].id]

  instance_types = ["t3.small"]

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }

  launch_template {
    name    = aws_launch_template.eks-with-disks.name
    version = aws_launch_template.eks-with-disks.latest_version
  }

  depends_on = [
    aws_iam_role_policy_attachment.terraform-node-AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.terraform-node-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.terraform-node-AmazonEC2ContainerRegistryReadOnly,
  ]
}

resource "aws_launch_template" "eks-with-disks" {
  name     = "lauch_template_${var.cluster-name}"
  key_name = var.key_name

  # network_interfaces {
  #   associate_public_ip_address = true
  # }

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "${var.cluster-name}_node"
    }
  }

  block_device_mappings {
    device_name = "/dev/sda1"

    ebs {
      volume_size = 20
      # volume_type = "gp2"
    }
  }
  # vpc_security_group_ids = [aws_security_group.demo-cluster.id]
  # user_data = filebase64("agent.sh")
  # user_data = base64encode(data.template_file.user_data.rendered)
}

