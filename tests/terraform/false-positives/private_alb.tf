resource "aws_security_group" "private_sg" {
  name = "private_sg"
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
resource "aws_lb" "internal_alb" {
  name = "internal-alb"
  internal = true
  security_groups = [aws_security_group.private_sg.id]
}
