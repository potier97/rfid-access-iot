output "iot_tf_backend_kms_key" {
  description = "ARN de llave para encriptar el backend de terra"
  value = aws_kms_key.iot_tf_backend_kms_key.arn
}