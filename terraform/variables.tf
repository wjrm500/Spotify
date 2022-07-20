variable "DB_HOST" {
  type = string
}

variable "DB_PORT" {
  type = string
}

variable "DB_USER" {
  type = string
}

variable "DB_PASSWORD" {
  type      = string
  sensitive = true
}