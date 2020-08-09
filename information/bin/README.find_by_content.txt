xxThis directory contiains shell tools to analyse couldtrail logs.
Json evnet records are selected by having any content anywhere
in the record matching the parameter searchglob.

Logs are assumed to be in a vault directory. Currently
vault logs need to be downloalded by hand using the
AWS console.

A config file, default.config can be used to supply
defaults for command line options.

[Default]
vault=vault
profile=scimma-aws-admin
loglevel=NORMAL

Shell users can construct simplw analysis filters.
using jq and sort, uniq, tabulate or even grep

Examples:

#find all json records in vault refering to July 1, 2020.
./find_by_content.py "2020-07-01*"

#make a formatted table of events, time, and assocated IP addressed.
./find_by_content.py "*"  | jq -r  "[.eventName,.eventTime,.sourceIPAddress] | @tsv" | tabulate

#find all json records in the vault in the first 5 days in july
./find_by_content.py "2020-07-0[1-6]*"

#Extract event names and display the most numerous events.
./find_by_content.py "2020-06*"  | jq ".eventName" | sort | uniq -c  | sort -n

#use GREP to explore file
./find_by_content.py "2020-06*"  | grep -i IPaddress
