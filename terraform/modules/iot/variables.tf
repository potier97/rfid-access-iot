variable "thing_name" {
  description = "Nombre del dispositivo IOT"
  type        = string
}

variable "thing_type_name" {
  description = "Tipo de dispositivo IOT"
  type        = string
}

variable "zone_thing_name" {
  description = "Nombre del grupo de dispositivos IOT"
  type        = string
}

# variable "thing_tags" {
#   description = "Etiquetas para el dispositivo IOT"
#   type        = map(string)
#   default     = {}
# }

variable "is_thing_sensor" {
  description = "Indica si el dispositivo IOT es un sensor"
  type        = bool
  default     = false
}

variable "thing_region" {
  description = "Region del dispositivo IOT"
  type        = string
}

variable "account" {
  description = "Cuenta de AWS"
  type        = string
}