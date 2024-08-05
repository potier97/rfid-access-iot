variable "backend_env" {
  type        = string
  description = "Ambiente al cual se esta haciendo referencia"
}

variable "bucket_backend_name" {
  type        = string
  description = "Nombre del bucket en s3 que controla la infra de terraform"
}

variable "bucket_backend_tags" {
  type        = map(any)
  description = "Etiquetas para distinguir el componente"
}

variable "kms_key_id" {
  type        = string
  description = "Id de la llave de encriptacion"
}

# ===================================================================
# ===================================================================
# ================= VARIABLES CONSTANTES PARA AWS ===================
# ===================================================================
# ===================================================================

variable "aws_region" {
  type        = string
  description = "Nombre del region de aws"
}

variable "aws_account" {
  type        = string
  description = "Cuenta de aws"
}

variable "aws_environment" {
  type        = string
  description = "Ambiente de los recursos"
}

variable "aws_tags" {
  type        = map(string)
  description = "Etiquetas generales para diferenciar la infra del sitio"
}

# ===================================================================
# ===================================================================
# ===================== RECURSOS DE IOT =============================
# ===================================================================
# ===================================================================

variable "thing_type_name" {
  description = "Nombre del tipo de dispositivo IOT"
  type        = string
}


variable "thing_type_description" {
  description = "Descripcion del tipo de dispositivo IOT"
  type        = string
}

variable "thing_type_searchable_attributes" {
  description = "Atributos de busqueda para el tipo de dispositivo IOT"
  type        = list(string)
  default     = []
}

variable "iot_tags" {
  description = "Etiquetas para el dispositivo IOT"
  type        = map(string)
  default     = {}
}

variable "iot_devices" {
  description = "Lista de dispositivos IOT"
  type = list(object({
    thing_name      = string
    zone_thing_name = string
    is_thing_sensor = bool
    thing_region    = string
  }))
  default = []
}

# ===================================================================
# ===================================================================
# ===================== RECURSOS DE DYNAMO ==========================
# ===================================================================
# ===================================================================

variable "dynamo_table_name" {
  description = "Nombre de la tabla de dynamo"
  type        = string

}

variable "dynamo_attribute_name" {
  description = "Nombre del atributo de la tabla de dynamoy hash_key"
  type        = string

}

# ===================================================================
# ===================================================================
# ===================== RECURSOS DE LAMBDA ==========================
# ===================================================================
# ===================================================================

variable "lambda_policy_name" {
  description = "Nombre de la politica de ejecucion de lambda"
  type        = string
}

variable "lambda_policy_description" {
  description = "Descripcion de la politica de ejecucion de lambda"
  type        = string
}

variable "lambdas_function" {
  description = "Lista de lambdas a crear"
  type = list(object({
    lambda_role_name   = string
    lambda_source_path = string
    lambda_output_path = string
    lambda_name        = string
    rule_name          = string
    rule_description   = string
    rule_sql           = string
  }))
  default = []
}
