# Definicion de un dispositivo IOT
resource "aws_iot_thing" "iot_tf_thing" {
  name            = "${var.thing_name}_${var.zone_thing_name}_${var.is_thing_sensor ? "rfid" : "door"}"
  thing_type_name = var.thing_type_name
  attributes = {
    zone = var.zone_thing_name
  }
}

resource "aws_iot_policy" "iot_tf_policy" {
  name = "iot_${var.thing_name}_${var.zone_thing_name}_${var.is_thing_sensor ? "rfid" : "door"}_policy"
  # Terraform's "jsonencode" function converts a
  policy = var.is_thing_sensor ? jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "iot:Connect",
        "Resource": "arn:aws:iot:${var.thing_region}:${var.account}:client/${var.thing_name}_rfid"
      },
      {
        "Effect": "Allow",
        "Action": "iot:Publish",
        "Resource": [
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/$aws/things/${var.thing_name}_rfid/shadow/update",
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/${var.thing_name}_rfid/${var.zone_thing_name}_group/rfid/open",
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/${var.thing_name}_rfid/${var.zone_thing_name}_group/rfid/remove",
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/${var.thing_name}_rfid/${var.zone_thing_name}_group/rfid/update",
          "arn:aws:iot:${var.thing_region}:${var.account}:client/${var.thing_name}_rfid"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "iot:Subscribe",
        "Resource": [
          "arn:aws:iot:${var.thing_region}:${var.account}:topicfilter/$aws/things/${var.thing_name}_rfid/shadow/update/delta",
          "arn:aws:iot:${var.thing_region}:${var.account}:topicfilter/${var.thing_name}_rfid/${var.zone_thing_name}_group/rfid/status"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "iot:Receive",
        "Resource": [
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/$aws/things/${var.thing_name}_rfid/shadow/update/delta",
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/${var.thing_name}_rfid/${var.zone_thing_name}_group/rfid/status"
        ]
      }
    ]
  }) : jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "iot:Connect",
        "Resource": "arn:aws:iot:${var.thing_region}:${var.account}:client/${var.thing_name}_door"
      },
      {
        "Effect": "Allow",
        "Action": "iot:Publish",
        "Resource": [
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/$aws/things/${var.thing_name}_door/shadow/update",
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/${var.thing_name}_door/${var.zone_thing_name}_group/door/*",
          "arn:aws:iot:${var.thing_region}:${var.account}:client/${var.thing_name}_door"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "iot:Subscribe",
        "Resource": [
          "arn:aws:iot:${var.thing_region}:${var.account}:topicfilter/$aws/things/${var.thing_name}_door/shadow/update/delta",
          "arn:aws:iot:${var.thing_region}:${var.account}:topicfilter/${var.thing_name}_door/${var.zone_thing_name}_group/door/*"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "iot:Receive",
        "Resource": [
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/$aws/things/${var.thing_name}_door/shadow/update/delta",
          "arn:aws:iot:${var.thing_region}:${var.account}:topic/${var.thing_name}_door/${var.zone_thing_name}_group/door/*"
        ]
      }
    ]
  })
}

resource "aws_iot_certificate" "iot_tf_cert" {
  active = true
}

resource "aws_iot_policy_attachment" "iot_tf_policy_attachments" {
  policy = aws_iot_policy.iot_tf_policy.name
  target = aws_iot_certificate.iot_tf_cert.arn
}

resource "aws_iot_thing_principal_attachment" "iot_tf_thing_att" {
  principal = aws_iot_certificate.iot_tf_cert.arn
  thing     = aws_iot_thing.iot_tf_thing.name
}


## ================================================================
## ================================================================
## ===========  Guardar recursos generados (accesos) ==============

resource "local_file" "iot_tf_device_certificates" {
  content  = aws_iot_certificate.iot_tf_cert.certificate_pem
  filename = "certs/${var.thing_name}_${var.zone_thing_name}_${var.is_thing_sensor ? "rfid" : "door"}/cert.pem.crt"
}

resource "local_file" "iot_tf_device_private_keys" {
  content  = aws_iot_certificate.iot_tf_cert.private_key
  filename = "certs/${var.thing_name}_${var.zone_thing_name}_${var.is_thing_sensor ? "rfid" : "door"}/private.pem.key"
}