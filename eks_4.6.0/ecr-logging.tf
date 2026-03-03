resource "aws_ecr_repository" "auto-ecr-log" {
  name                 = var.terraform-ecr-log
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}