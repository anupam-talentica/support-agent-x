variable "enabled" {
  description = "Whether the distribution is enabled"
  type        = bool
  default     = true
}

variable "is_ipv6_enabled" {
  description = "Whether the IPv6 is enabled for the distribution"
  type        = bool
  default     = true
}

variable "comment" {
  description = "Any comments you want to include about the distribution"
  type        = string
  default     = "CloudFront distribution for agentx"
}

variable "default_root_object" {
  description = "The object that you want CloudFront to return when an end user requests the root URL"
  type        = string
  default     = "index.html"
}

variable "origin_domain_name" {
  description = "The DNS domain name of the S3 bucket or another origin"
  type        = string
}

variable "origin_id" {
  description = "A unique identifier for the origin"
  type        = string
}

variable "origin_access_identity" {
  description = "The CloudFront origin access identity to associate with the origin"
  type        = string
  default     = null
}

variable "allowed_methods" {
  description = "Controls which HTTP methods CloudFront processes and forwards to your Amazon S3 bucket or your custom origin"
  type        = list(string)
  default     = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
}

variable "cached_methods" {
  description = "Controls whether CloudFront caches the response to requests using the specified HTTP methods"
  type        = list(string)
  default     = ["GET", "HEAD"]
}

variable "forward_query_string" {
  description = "Indicates whether you want CloudFront to forward query strings to the origin"
  type        = bool
  default     = false
}

variable "forward_cookies" {
  description = "Specifies whether you want CloudFront to forward cookies to the origin"
  type        = string
  default     = "none"
}

variable "viewer_protocol_policy" {
  description = "Use this element to specify the protocol that users can use to access the files in the origin"
  type        = string
  default     = "redirect-to-https"
}

variable "min_ttl" {
  description = "The minimum amount of time that you want objects to stay in CloudFront caches"
  type        = number
  default     = 0
}

variable "default_ttl" {
  description = "The default amount of time (in seconds) that an object is in a CloudFront cache"
  type        = number
  default     = 86400
}

variable "max_ttl" {
  description = "The maximum amount of time (in seconds) that an object is in a CloudFront cache"
  type        = number
  default     = 31536000
}

variable "geo_restriction_type" {
  description = "The method that you want to use to restrict distribution of your content by country"
  type        = string
  default     = "none"
}

variable "geo_restriction_locations" {
  description = "The ISO 3166-1-alpha-2 codes for which you want CloudFront either to distribute your content or not"
  type        = list(string)
  default     = []
}

variable "cloudfront_default_certificate" {
  description = "Whether you want CloudFront to use the default certificate"
  type        = bool
  default     = true
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
  default     = {}
} 