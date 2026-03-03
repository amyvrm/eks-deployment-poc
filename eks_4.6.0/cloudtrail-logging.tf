#data "aws_caller_identity" "current" {}
#
#resource "aws_cloudtrail" "terraform-cloudtrail" {
#  name                          = var.terraform-cloudtrail
#  s3_bucket_name                = var.s3-bucket
#  s3_key_prefix                 = var.s3-prefix
#  include_global_service_events = false
#  depends_on = [aws_s3_bucket_policy.default]
#}
#
#resource "aws_s3_bucket_policy" "default" {
#  bucket = var.s3-bucket
#  policy = <<POLICY
#{
#    "Version": "2012-10-17",
#    "Statement": [
#        {
#            "Sid": "AWSCloudTrailAclCheck",
#            "Effect": "Allow",
#            "Principal": {
#              "Service": "cloudtrail.amazonaws.com"
#            },
#            "Action": "s3:GetBucketAcl",
#            "Resource": "arn:aws:s3:::${var.s3-bucket}"
#        },
#        {
#            "Sid": "AWSCloudTrailWrite",
#            "Effect": "Allow",
#            "Principal": {
#              "Service": "cloudtrail.amazonaws.com"
#            },
#            "Action": "s3:PutObject",
#            "Resource": "arn:aws:s3:::${var.s3-bucket}/${var.s3-prefix}/*",
#            "Condition": {
#                "StringEquals": {
#                    "s3:x-amz-acl": "bucket-owner-full-control"
#                }
#            }
#        }
#    ]
#}
#POLICY
#}