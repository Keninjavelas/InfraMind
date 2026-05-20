resource "aws_iam_policy" "super_admin" {
  policy = jsonencode({
    Statement = [{ Action = "*", Effect = "Allow", Resource = "*" }]
  })
}
