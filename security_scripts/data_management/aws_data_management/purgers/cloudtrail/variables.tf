
variable "standard_tags" {

  description = "standard tags' applied to all taggable resources"
  type        = map(string)
  default  = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/security-scripts",
                 "lifetime":"forever",
                 "Service":"opsLogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Production",
                 "Name":"purge cloudtail"

                 }

}


