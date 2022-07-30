variable "DB_HOST" {
  type = string
}

variable "DB_PORT" {
  type = number
}

variable "DB_USER" {
  type = string
}

variable "DB_PASSWORD" {
  type      = string
  sensitive = true
}

variable "VPC_SUBNET_IDS" {
    type = list(string)
}

variable "VPC_SECURITY_GROUP_IDS" {
    type = list(string)
}