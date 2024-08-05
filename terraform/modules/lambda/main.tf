// Codigo basado en:
// https://spacelift.io/blog/terraform-aws-lambda

resource "aws_iam_role" "iot_tf_lambda_role" {
  name = "${var.lambda_role_name}_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com",
      },
    }],
  })

  tags = merge(var.aws_tags, {
    Name = "${var.lambda_role_name}_role"
  })
}

resource "aws_iam_role_policy_attachment" "iot_tf_lambda_policy_attachment" {
  role       = aws_iam_role.iot_tf_lambda_role.name
  policy_arn = var.lambda_policy_arn
}

data "archive_file" "iot_tf_lambda_open" {
  type        = "zip"
  source_dir  = var.lambda_source_path
  output_path = var.lambda_output_path
}

resource "aws_lambda_function" "iot_tf_lambda_function" {
  filename         = data.archive_file.iot_tf_lambda_open.output_path
  function_name    = var.lambda_name
  role             = aws_iam_role.iot_tf_lambda_role.arn
  handler          = "index.handler"
  runtime          = "nodejs20.x"
  source_code_hash = filebase64sha256(data.archive_file.iot_tf_lambda_open.output_path)

  environment {
    variables = {
      DYNAMODB_TABLE = var.dynamodb_table_name
      # AWS_REGION     = var.aws_region
    }
  }

  tags = merge(var.aws_tags, {
    Name = var.lambda_name
  })
}

resource "aws_lambda_alias" "iot_tf_lambda_alias" {
  name             = "${var.lambda_name}_alias"
  description      = "Versión de la lambda ${var.lambda_name} desplegada"
  function_name    = aws_lambda_function.iot_tf_lambda_function.function_name
  function_version = "$LATEST"
}

resource "aws_iot_topic_rule" "iot_tf_rule_lambda_function" {
  name        = "${var.rule_name}_rule"
  description = var.rule_description
  enabled     = true
  sql         = var.rule_sql
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.iot_tf_lambda_function.arn
  }
}

resource "aws_lambda_permission" "iot_tf_function_permission" {
  # statement_id  = "${var.lambda_name}_AllowIoTInvokeOpen"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.iot_tf_lambda_function.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.iot_tf_rule_lambda_function.arn
}