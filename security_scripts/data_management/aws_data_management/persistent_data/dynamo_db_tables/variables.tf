
//
// All the varibles below are to be furnaied by the
// insitantiaing moddule.  (eg Main from production or development)
//

variable "standard_tags" {

  description = "standard tags applied to all taggable resources"
  type        = map(string)
}


variable "table_name" {
  type        = string
  description = "name of dynamom DB table holding the processed logs"
}

variable "dynamodb_put_item_policy_name" {
  type        = string
  description = "Names the policy alloing logging to the dynamo DB Table"
}

