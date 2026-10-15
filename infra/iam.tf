resource "aws_iam_policy" "pipeline_s3" {
  name        = "off-pipeline-s3-access"
  description = "Least-privilege S3 access for the Open Food Facts pipeline"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::${var.bucket_name}"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "arn:aws:s3:::${var.bucket_name}/*"
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "pipeline" {
  name = "off-pipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { AWS = data.aws_caller_identity.current.arn }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "pipeline_s3" {
  role       = aws_iam_role.pipeline.name
  policy_arn = aws_iam_policy.pipeline_s3.arn
}