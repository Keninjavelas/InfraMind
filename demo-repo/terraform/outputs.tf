output "alb_dns_name" {
  value       = aws_alb.web_alb.dns_name
  description = "The public DNS name of the ALB"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.public_assets.arn
  description = "The ARN of the public S3 bucket"
}
