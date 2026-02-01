locals {
  policy_document = var.policy_json != null ? var.policy_json : file(var.policy_json_path)
}

resource "aws_iam_policy" "this" {
  name        = var.policy_name
  description = var.policy_description
  policy      = local.policy_document

  tags = var.tags
}


# Look up for existing role
data "aws_iam_role" "this" {
  count = var.attach_to_role && var.role_name != null ? 1 : 0
  name  = var.role_name
}

resource "aws_iam_role_policy_attachment" "this" {
  count = var.attach_to_role ? 1 : 0

  role       = data.aws_iam_role.this[0].name
  policy_arn = aws_iam_policy.this.arn
}

resource "aws_iam_user_policy_attachment" "this" {
  count      = var.attach_to_user ? 1 : 0
  user       = var.user_name
  policy_arn = aws_iam_policy.this.arn
}



/*
resource "aws_iam_role_policy_attachment" "this" {
  count      = var.attach_to_role ? 1 : 0
  role       = var.role_name
  policy_arn = aws_iam_policy.this.arn
}

resource "aws_iam_user_policy_attachment" "this" {
  count      = var.attach_to_user ? 1 : 0
  user       = var.user_name
  policy_arn = aws_iam_policy.this.arn
} */