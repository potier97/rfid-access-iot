## ================================================
## ====== VARIABLES DEL BUCKET BACKEND ============
## ================================================
backend_env         = "develop"
bucket_backend_name = "example-bucket-backend"
bucket_backend_tags = {
  Environment = "Develop",
  Name        = "example-bucket-backend",
  Proyect     = "IOT-RFID"
  CreatedBy   = "Terraform",
}
kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/EXAMPLE-KEY-ID"
## =================================================================
## ========= VARIABLES GENERALES PARA TODOS LOS MODULOS ============
## =================================================================
aws_region      = "us-east-1"
aws_account     = "123456789012"
aws_environment = "develop"
aws_tags = {
  Environment = "develop",
  Version     = "2.0.0"
  Proyect     = "IOT-RFID"
  Origin      = "Terraform"
  Owner       = "User"
}

## =================================================================
## ================== VALORES DE LOS RESURSOS ======================
## =================================================================

thing_type_name                  = "iot_access_control"
thing_type_description           = "Dispositivo de control de acceso para zonas"
thing_type_searchable_attributes = ["zone"]
iot_tags = {
  Environment = "develop",
  Version     = "2.0.0"
  Proyect     = "IOT-RFID"
  Origin      = "Terraform"
  Owner       = "User"
}

iot_devices = [
  {
    thing_name      = "example-thing-id-1"
    zone_thing_name = "0001"
    is_thing_sensor = false
    thing_region    = "us-east-1"
  },
  {
    thing_name      = "example-thing-id-2"
    zone_thing_name = "0001"
    is_thing_sensor = false
    thing_region    = "us-east-1"
  },
  {
    thing_name      = "example-thing-id-3"
    zone_thing_name = "0001"
    is_thing_sensor = true
    thing_region    = "us-east-1"
  },
]

## =================================================================
## ============ VALORES DE LOS RESURSOS DYANMO DB ==================
## =================================================================
dynamo_table_name = "example-table-name"
dynamo_attribute_name = "CardID"

## =================================================================
## ============ VALORES DE LOS RESURSOS LAMBDA =====================
## =================================================================

lambda_policy_name = "example-lambda-policy"
lambda_policy_description = "Politica de ejecucion de lambda para acceso a dynamo"
lambdas_function = [
  {
    lambda_name = "example-lambda-card"
    lambda_output_path = "zip/access.zip"
    lambda_source_path = "lambdas/access"
    lambda_role_name = "lambda_access_execution_role"
    rule_name = "example_rule_door"
    rule_description = "Regla de solicitud de apertura de puerta"
    rule_sql = "SELECT * FROM '+/+/rfid/open' WHERE uid <> NULL AND type <> NULL AND group <> NULL"
  },
  {
    lambda_name = "example-lambda-update-card"
    lambda_output_path = "zip/update.zip"
    lambda_source_path = "lambdas/update"
    lambda_role_name = "lambda_update_execution_role"
    rule_name = "example_rule_update_card"
    rule_description = "Regla de solicitud de actualizacion/creacion de tarjeta en base de datos"
    rule_sql = "SELECT * FROM '+/+/rfid/update' WHERE uid <> NULL AND type <> NULL AND group <> NULL"
  },
  {
    lambda_name = "example-lambda-remove-card"
    lambda_output_path = "zip/remove.zip"
    lambda_source_path = "lambdas/remove"
    lambda_role_name = "lambda_remove_execution_role"
    rule_name = "example_rule_remove_card"
    rule_description = "Regla de solicitud de eliminacion de tarjeta en base de datos"
    rule_sql = "SELECT * FROM '+/+/rfid/remove' WHERE uid <> NULL AND type <> NULL AND group <> NULL"
  },
]
