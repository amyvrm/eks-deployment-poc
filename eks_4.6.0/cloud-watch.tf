#resource "aws_flow_log" "terraform-flow-log" {
#  iam_role_arn    = aws_iam_role.terraform-vpc-iam.arn
#  log_destination = aws_cloudwatch_log_group.terraform-log.arn
#  traffic_type    = "ALL"
#  vpc_id          = aws_vpc.terraform-vpc.id
#}

#resource "aws_cloudwatch_log_group" "terraform-log" {
#  # The log group name format is /aws/eks/<cluster-name>/cluster
#  # Reference: https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html
#  name              = "/aws/eks/${var.cluster-name}/cluster"
#  retention_in_days = 14
#
#  # ... potentially other configuration ...
#}

#resource "aws_iam_role" "terraform-vpc-iam" {
#  name = "terraform-vpc-iam"
#
#  assume_role_policy = <<EOF
#{
#  "Version": "2012-10-17",
#  "Statement": [
#    {
#      "Sid": "",
#      "Effect": "Allow",
#      "Principal": {
#        "Service": "vpc-flow-logs.amazonaws.com"
#      },
#      "Action": "sts:AssumeRole"
#    }
#  ]
#}
#EOF
#}
#
#resource "aws_iam_role_policy" "terraform-log-policy" {
#  name = "terraform-log-policy"
#  role = aws_iam_role.terraform-vpc-iam.id
#
#  policy = <<EOF
#{
#  "Version": "2012-10-17",
#  "Statement": [
#    {
#      "Action": [
#        "logs:CreateLogGroup",
#        "logs:CreateLogStream",
#        "logs:PutLogEvents",
#        "logs:DescribeLogGroups",
#        "logs:DescribeLogStreams"
#      ],
#      "Effect": "Allow",
#      "Resource": "*"
#    }
#  ]
#}
#EOF
#}