# AWS Provider configuration
provider "aws" {
  region = "us-east-1"
}

# HIGH: public S3 bucket
resource "aws_s3_bucket" "public_assets" {
  bucket = "inframind-demo-public-assets-bucket"
  acl    = "public-read"

  tags = {
    Name = "Public Assets Bucket"
  }
}

# PUBLIC: ALB (application load balancer)
resource "aws_alb" "web_alb" {
  name               = "demo-web-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.allow_ssh.id]
  subnets            = [aws_subnet.public.id]
}

resource "aws_lb_target_group" "ecs_tg" {
  name     = "ecs-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_alb.web_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}

resource "aws_ecs_cluster" "main_cluster" {
  name = "demo-ecs-cluster"
}

resource "aws_ecs_task_definition" "web_task" {
  family                   = "web-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = <<EOF
[
  {
    "name": "web-app",
    "image": "nginx:latest",
    "essential": true,
    "portMappings": [
      {
        "containerPort": 80,
        "hostPort": 80
      }
    ],
    "environment": [
      {
        "name": "DATABASE_URL",
        "value": "aws_db_instance.database.endpoint"
      }
    ]
  }
]
EOF
}

resource "aws_ecs_service" "web_service" {
  name            = "demo-web-service"
  cluster         = aws_ecs_cluster.main_cluster.id
  task_definition = aws_ecs_task_definition.web_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public.id]
    security_groups  = [aws_security_group.allow_ssh.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg.arn
    container_name   = "web-app"
    container_port   = 80
  }

  depends_on = [aws_lb_listener.http_listener]
}

resource "aws_db_instance" "database" {
  allocated_storage   = 20
  db_name             = "demodb"
  engine              = "postgres"
  engine_version      = "15"
  instance_class      = "db.t3.micro"
  username            = "dbuser"
  password            = "SuperSecretPassword123!"
  publicly_accessible = false
  skip_final_snapshot = true
}
