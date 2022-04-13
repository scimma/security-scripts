
variable "standard_tags" {
  default     = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/securit-scripts",
                 "lifetime":"forever",
                 "Service":"postgresdlogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Development",
                 "Name":"TBD"
}

  description = "standard tags' applied to all taggable resources"
  type        = map(string)
}

variable "table_name" {
         type = string
         default = "PostgresLogs_devel"
         description = "dynamo DB table name -- devel should not pollute production"
}