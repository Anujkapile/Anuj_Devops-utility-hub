output "ec2_public_ip" {
  value = aws_instance.devops_hub.public_ip
}

output "putty_connection" {
  value = "Use PuTTY with key devops-key.ppk to connect to ubuntu@${aws_instance.devops_hub.public_ip}"
}