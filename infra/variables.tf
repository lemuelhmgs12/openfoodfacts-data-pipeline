variable "aws_region" {
  type        = string
  description = "AWS region for all resources"
}

variable "bucket_name" {
  type        = string
  description = "Existing S3 bucket the pipeline reads and writes"
}