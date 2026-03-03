resource "aws_security_group_rule" "workstation-ssh-rule" {
  cidr_blocks       = [local.workstation-external-cidr]
  description       = "Allow workstation to communicate with the cluster"
  from_port         = 22
  protocol          = "tcp"
  security_group_id = var.sgid
  to_port           = 22
  type              = "ingress"
}


resource "null_resource" "install" {
  depends_on = [aws_security_group_rule.workstation-ssh-rule]

  connection {
    type = "ssh"
    host     = var.ip
    timeout  = "3m"
    user     = "ec2-user"
    private_key = file("${var.path}/${var.key_name}.pem")
  }

  # Copies all files and folders
  provisioner "file" {
      source      = "${var.path}/agent.sh"
      destination = "/tmp/agent.sh"
  }

  provisioner "remote-exec" {
      inline = [
          "sudo hostnamectl set-hostname production.compute.machine",
          "chmod +x /tmp/agent.sh",
          "sudo sh /tmp/agent.sh ${var.policy_id} ${var.comp_grp}"
      ]
  }
}

output "sgip" {
	value = "${local.workstation-external-cidr}"
}