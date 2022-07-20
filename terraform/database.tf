resource "aws_db_instance" "my_database" {
  allocated_storage    = 10
  db_name              = "my_database"
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t3.micro"
  username             = var.DB_USER
  password             = var.DB_PASSWORD
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
}