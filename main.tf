# Define the AWS provider

variable "bucket" {
  default = "the-cloud-shepherd-csv-linkedin"
}

provider "aws" {
  region = "us-east-1"
}

# Define the S3 bucket for storing the CSV files
resource "aws_s3_bucket" "csv_bucket" {
  bucket = var.bucket
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.csv_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "*",
        Resource = "${aws_s3_bucket.csv_bucket.arn}/*"
      }
    ]
  })
}

# # Define the Lambda function resource
resource "aws_lambda_function" "csv_to_json" {
  function_name = "csv-to-json"
  filename = "lambda_payload.zip"
  source_code_hash = filebase64sha256("lambda_payload.zip")
  handler = "lambda_handler.lambda_handler"
  role = aws_iam_role.lambda.arn
  runtime = "python3.9"
}

# Define the IAM role for the Lambda function
resource "aws_iam_role" "lambda" {
  name = "lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Define the IAM policy for the Lambda function
resource "aws_iam_policy" "lambda" {
  name = "lambda-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:GetObject",
          "connect:*"
          

        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

# # Attach the IAM policy to the IAM role

resource "aws_iam_role_policy_attachment" "lambda" {
  policy_arn = aws_iam_policy.lambda.arn
  role = aws_iam_role.lambda.name
}

# Define the S3 bucket notification configuration
resource "aws_s3_bucket_notification" "csv_to_json" {
    depends_on = [ aws_lambda_permission.allow_bucket ]
    bucket = aws_s3_bucket.csv_bucket.id
#   bucket = var.bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.csv_to_json.arn
    events              = ["s3:ObjectCreated:*"]
    # filter_prefix       = "csv/"
    filter_suffix       = ".csv"
  }

  
}

#this is required r
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.csv_to_json.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.csv_bucket.arn
}



