provider "aws" {
  profile = "profile2024"
  region  = "us-east-1"
}

# ============================================
# === SERVICIOS DECLARADOS PARA EL BACKEND ===
# ============================================

# GENERAR LLAVE DE ENCRIPTADO
resource "aws_kms_key" "iot_tf_backend_kms_key" {
  description             = "Llave para encriptar datos de los objetos de los buckets"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  lifecycle {
    prevent_destroy = true
  }
}

# ALIAS DE LA LLAVE
resource "aws_kms_alias" "iot_tf_backend_kms_key" {
  name          = "alias/iot_kms_backend_key_alias"
  target_key_id = aws_kms_key.iot_tf_backend_kms_key.key_id
  lifecycle {
    prevent_destroy = true
  }
}

# Backend para el control de la infraestructura
resource "aws_s3_bucket" "iot_tf_backend_s3_bucket" {
  bucket = var.bucket_backend_name
  tags   = var.bucket_backend_tags
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "iot_tf_backend_sse_config" {
  bucket = aws_s3_bucket.iot_tf_backend_s3_bucket.id
  # Regla de encriptacion
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.iot_tf_backend_kms_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# ================================================================
# ================================================================
# ======= MODULO PARA CREAR DEFINICION DE DISPOSITIVOS IOT =======
# ================================================================
# ================================================================

# Definicion de un tipo de dispositivo IOT
resource "aws_iot_thing_type" "iot_tf_thing_type" {
  name = var.thing_type_name
  properties {
    description           = var.thing_type_description
    searchable_attributes = var.thing_type_searchable_attributes
  }
  tags = merge(var.aws_tags, var.iot_tags)
}

# Definicion de un dispositivo IOT
module "iot" {
  source          = "./modules/iot"
  for_each        = { for instance in var.iot_devices : instance.thing_name => instance }
  thing_name      = each.value.thing_name
  thing_type_name = aws_iot_thing_type.iot_tf_thing_type.name
  zone_thing_name = each.value.zone_thing_name
  is_thing_sensor = each.value.is_thing_sensor
  thing_region    = each.value.thing_region
  account         = var.aws_account
}

# ================================================================
# ================================================================
# =================== DYNAMO DB PARA IOT =========================
# ================================================================
# ================================================================

resource "aws_dynamodb_table" "iot_tf_dynamo_table" {
  name         = var.dynamo_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = var.dynamo_attribute_name

  attribute {
    name = var.dynamo_attribute_name
    type = "S"
  }
  tags = merge(var.aws_tags, {
    Name = var.dynamo_table_name
  })
}

# ================================================================
# ================================================================
# =================== MODULO PARA CREAR LAMBDA  ==================
# ================================================================
# ================================================================

resource "aws_iam_policy" "iot_tf_lambda_policy" {
  name        = "${var.lambda_policy_name}_policy"
  description = var.lambda_policy_description
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups"
        ],
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:GetItem"
        ],
        Resource = aws_dynamodb_table.iot_tf_dynamo_table.arn
      },
      {
        Effect = "Allow",
        Action = [
          "iot:Publish"
        ],
        Resource = [
          "arn:aws:iot:${var.aws_region}:${var.aws_account}:topic/*",
          # "arn:aws:iot:${var.aws_region}:${var.aws_account}:topic/*_door/*_group/rfid/close"
        ]
      }
    ]
  })
}

module "lambda" {
  source              = "./modules/lambda"
  for_each            = { for instance in var.lambdas_function : instance.lambda_name => instance }
  lambda_role_name    = each.value.lambda_role_name
  aws_tags            = var.aws_tags
  aws_region          = var.aws_region
  lambda_policy_arn   = aws_iam_policy.iot_tf_lambda_policy.arn
  lambda_source_path  = each.value.lambda_source_path
  lambda_output_path  = each.value.lambda_output_path
  lambda_name         = each.value.lambda_name
  dynamodb_table_name = aws_dynamodb_table.iot_tf_dynamo_table.name
  rule_name           = each.value.rule_name
  rule_description    = each.value.rule_description
  rule_sql            = each.value.rule_sql
}
