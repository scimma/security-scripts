# scimma-security-scripts
Set of scripts to rapidly administer AWS activities. These can be run from the pip package (link) or in raw .py form

## Prerequisites
* Python 3.x
* AWS CLI (with credentials file)
* api.github.com auth token in ~/.netrc in format
<code>machine api.github.com login %user% password %access token%</code>. Get yours [here](https://github.com/settings/tokens).
* jq
* Windows or *nix machine

## Installation
To install this script on a system level, run `pip install scimma-security-scripts`.
To run them raw, download from the official repository. 

## Available subcommands
When installed with pip, the scripts can be run with an `sc {subcommand}` command, and available arguments can be retrieved with `sc {subcommand} -h`. 

#### sc inf_find
Dump cloudtail json event records from the vault having some value matching the globstring.

A vault file is a dictionary of "Records" containing an array of json objects, one json object per cloudtrail event. There is a large variety of events, each with a different json schema.

Shell users can construct simple analysis filters using jq and sort, uniq, tabulate or even grep

Examples:

|Use|Command|
| --- | ---|
|find all json records in vault referring to July 1, 2020|<code>sc inf_find "2020-07-01*"</code>|
|find all json records in vault describing actions taken by user named "petravic" in the first week of August|<code>sc inf_find -da 2020-08-01 -dd 6 "\*petravic*"</code>|
|make a formatted table of events, time, and assocated IP addressed.|<code>sc inf_find "*" &#124; jq -r  "[.eventName,.eventTime,.sourceIPAddress] &#124; @tsv" &#124; tabulate</code>|
|find all json records in the vault in the first 6 days in august|<code>sc inf_find "2020-08-0[1-6]*"</code>|
|extract event names and display the most numerous events.|<code>sc inf_find "2020-06*" &#124; jq ".eventName" &#124; sort &#124; uniq -c  &#124; sort -n</code>|
|use GREP to explore file|<code>sc inf_find "2020-06*" &#124; grep -i IPaddress</code>|

#### sc inf_report
Run tag, s3, secret, certificate, repo inventory reports

#### sc inf_vault
Download Cloudtrail logs to the vault directory. Downloads are incremental -- previous downloads are not
re-fetched or deleted.

A vault file is bushy directory tree that is stored under $HOME/.vault. the leaves are (many json) files, each covering a small slice of time. The files contain AWS event records.

Other tools (notably find_by_content.py) based
on trailscraper use the downloaded data for analysis.

#### sc x_report
Similar to Duo's Cloudmapper, but it ingests more, graphs more, and uses tags to graph

#### sc control_audit
Run audits checking system dependencies, policies attached to the target role, caller's privileges if sufficient, repository state, roles existing in account, and caller's identity.

#### sc control_green_button
Strip all policies from target role and attach ProposedPoweruser and RoleManagementWithCondition

#### sc control_red_button
Strip all policies from target role and stop all EC2 instances in all regions

#### sc test_green_button
Simulate green button functionality

#### sc test_red_button
Simulate red button functionality

## Config file
When invoked with `sc` command, the script will pull default arguments from a built-in *default.cfg* file. The console interface also checks for a file specified through the `$SCIMMA_SECURITY_CFG` variable.

This variable is auto-created if it's not detected, and can be modified by editing *~/.bash_profile* (bash), *~/.zshenv* (zsh), or running `SETX SCIMMA_SECURITY_CFG "path/config.cfg" /M` (cmd). The expected config file format is such:

<pre>[DEFAULT]
profile=scimma-uiuc-aws-admin
role=scimma_power_user
vaultdir=~/.vault
loglevel=NORMAL

# info tools
[TAG_REPORT]
dbfile=:memory:
[DOWNLOAD]
bucket=s3://scimma-processes/Scimma-event-trail
accountid=585193511743</pre>

## Running the scripts raw
While not intended to be a primary way of running, the scripts can be executed individually. For example:
`python find_by_content.py -dd 14 *petravic*`

Is equivalent to 

`sc inf_find -dd 14 *petravic*`



