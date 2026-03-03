resource "aws_flow_log" "terraform-flow-log" {
  log_destination      = "arn:aws:s3:::${var.s3-bucket}/vpc-log/"
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.terraform-vpc.id
}