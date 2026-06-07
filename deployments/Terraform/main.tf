provider "aws" {
  region = "ap-south-1"   # Mumbai — change if needed
}
#===================Security Group: APP SERVER=1 ===========================================================================
resource "aws_security_group" "anuj_sg" {
  name        = "anuj"
  description = "Allow SSH, HTTP, HTTPS, 5000"
  vpc_id = "vpc-00ed19a1c09f13a9d"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # Jenkins
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # Flask app
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
#=================EC2:App server============================================================

resource "aws_instance" "devops_hub" {
  ami                    = "ami-0a14f53a6fe4dfcd1"  # Ubuntu 22.04 ap-south-1
  instance_type          = "t2.micro"
  key_name               = "devops-key"
  vpc_security_group_ids = [aws_security_group.anuj_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "DevOpsUtilityHub"
}

}
#===================Security Group: APP SERVER=2 ==========================================================================

resource "aws_security_group" "jenkins_sg" {
  name        = "jenkins_sg"
  description = "Jenkins + SSH"
  vpc_id      = "vpc-00ed19a1c09f13a9d"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 50000
    to_port     = 50000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
# ─── EC2: Jenkins Server ─────────────────────────────────────────────

resource "aws_instance" "jenkins_sg" {
  ami           = "ami-0a14f53a6fe4dfcd1"
  instance_type = "t2.micro"
  key_name      = "devops-key"
  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }
  tags = { 
    Name = "JenkinsCICD"  
    }
}
#==============================================================
#===================Security Group: APP SERVER===========================================================================
resource "aws_security_group" "monitoring_sg" {
  name        = "monitoring-sg"
  description = "Allow SSH, HTTP, HTTPS, 5000"
  vpc_id = "vpc-00ed19a1c09f13a9d"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # Jenkins
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # Flask app
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
#=================EC2:App server============================================================

resource "aws_instance" "monitoring" {
  ami                    = "ami-0a14f53a6fe4dfcd1"  # Ubuntu 22.04 ap-south-1
  instance_type          = "t2.micro"
  key_name               = "devops-key"
  vpc_security_group_ids = [aws_security_group.monitoring_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "Monitoring_Server"
}

}
