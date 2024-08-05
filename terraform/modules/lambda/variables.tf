variable "lambda_role_name" {
  description = "Nombre del rol de ejecucion de lambda"
  type        = string
}

variable "aws_tags" {
  type        = map(string)
  description = "Etiquetas generales para diferenciar la infra del sitio"
}

variable "aws_region" {
  type        = string
  description = "Region de AWS"
}

variable "lambda_policy_arn" {
  type        = string
  description = "ARN de la politica de ejecucion de lambda"
}

variable "lambda_source_path" {
  type        = string
  description = "Ruta del codigo fuente de la lambda"
}

variable "lambda_output_path" {
  type        = string
  description = "Ruta de salida del archivo zip de la lambda"
}

variable "lambda_name" {
  type        = string
  description = "Nombre de la lambda"
}

variable "dynamodb_table_name" {  
  type        = string
  description = "Nombre de la tabla de dynamo"
}

variable "rule_name" {
  type        = string
  description = "Nombre de la regla que se ejecuta en iot core"
}

variable "rule_description" {
  type        = string
  description = "Descripcion de la regla que se ejecuta en iot core"
}

variable "rule_sql" {
  type        = string
  description = "SQL de la regla que se ejecuta en iot core"
}