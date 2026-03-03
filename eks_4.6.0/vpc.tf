#
# VPC Resources
#  * VPC
#  * Subnets
#  * Internet Gateway
#  * Route Table
#

resource "aws_vpc" "terraform-vpc" {
  cidr_block = "10.0.0.0/16"

  tags = tomap({
    "Name"                                      = var.terraform-vpc,
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_subnet" "terraform-subnet" {
  count = 2

  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.terraform-vpc.id

  tags = tomap({
    "Name"                                      = var.terraform-vpc,
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_internet_gateway" "terraform-gateway" {
  vpc_id = aws_vpc.terraform-vpc.id

  tags = {
    Name = var.terraform-gateway
  }
}

resource "aws_route_table" "terraform-route-table" {
  vpc_id = aws_vpc.terraform-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.terraform-gateway.id
  }
}

resource "aws_route_table_association" "terraform-table-ass" {
  count = 2

  subnet_id      = aws_subnet.terraform-subnet.*.id[count.index]
  route_table_id = aws_route_table.terraform-route-table.id
}

#resource "aws_nat_gateway" "terraform-nat-gateway" {
#  count         = 2
#  allocation_id = "eipalloc-0d382e2ebc1bc55b9"
#  subnet_id     = aws_subnet.terraform-subnet.*.id[count.index]
#
#  tags = {
#    Name = "terraform-nat-gateway-${count.index}"
#  }
#
#  # To ensure proper ordering, it is recommended to add an explicit dependency
#  # on the Internet Gateway for the VPC.
#  depends_on = [aws_internet_gateway.terraform-gateway]
#}
