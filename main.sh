#!/bin/sh

# init by making scripts executable
chmod 755 Buttons/*.sh
chmod 755 Audit/*.sh
chmod 755 Theater/*.sh

# defaults -- provide them up here, and they can be used in the help printoutrepository= ~donaldp/
role=scimma_test_power_user
profile=scimma-uiuc-aws-admin


printHelp () {
cat - <<EOF
Security scripts for SCiMMA AWS
Options
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -b     button to toggle: RED, YELLOW or GREEN
   -p     CLI profile to use (default: ${profile})
   -r     role to apply the button to (default: ${role})
   -e     enable the specified button
   -t     TODO: test mode "dry run" button engagement that simulates -e command
   -a     audit mode
            possible audits:
            all - run all audits
            dependencies - checks for dependencies installed
            repo - checks if repo is up to date and consistency
            myprivileges - checks if current AWS CLI user has sufficient privileges
            policies - checks what policies the target AWS role has
            roles - lists all IAM roles and their descriptions
            whoami - describes current user
EOF
}

buttonEnable () {
  case $1 in
    RED)    ./Buttons/depriv.sh -r $2 -p $3; ./Buttons/ec2stop.sh -p $3 ;;
    YELLOW) echo "yellow button not implemented yet" ;;
    GREEN)  ./Buttons/priv.sh -r $2 -p $3 ;;
  esac
  echo "$1 button engaged"
}

buttonTheater () {
  case $1 in
    RED)    ./Theater/red.sh -r $2 -p $3 ; ./Theater/ec2fake.sh -p $3 ;;
    YELLOW) echo "yellow button not implemented yet" ;;
    GREEN)  ./Theater/green.sh -r $2 -p $3 ;;
  esac
  echo "$1 simulated"
}

auditRun () {
  case $1 in
    all) auditRun dependencies; auditRun myprivileges $2 $3; auditRun policies $2 $3; auditRun whoami $2 $3; auditRun roles $2 $3; auditRun repo $2 $3 ;;
    dependencies) ./Audit/dependencies.sh ;;
    myprivileges) ./Audit/privileges.sh -p $3;;
    policies) ./Audit/policies.sh -r $2 -p $3;;
    whoami) ./Audit/whoami.sh -p $3;;
    roles) ./Audit/roles.sh -p $3;;
    repo) git remote show origin ;;
  esac
  echo "$1 audit complete"
  echo "_________________"
}

# option processing  $OPTARG fetches the argument
while getopts hxb:p:r:eta: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      b) button=$OPTARG ;;
      p) profile=$OPTARG ;;
      r) role=$OPTARG ;;
      e) action=ENABLE ;;
      t) action=THEATER ;;
      a) audit=$OPTARG ;;
      *) printHelp; exit 1 ;;
  esac;
done
if [ $OPTIND -eq 1 ]; then printHelp ; exit 0; fi

#get rid of processed  options $* is now arguements.
shift `expr $OPTIND - 1`


# audit scripts
if [ -n "$audit" ]; then
  case $audit in
    all) echo "All audits will be run" ; auditRun all $role $profile ;;
    policies) echo "$audit audit will be run" ; auditRun $audit $role $profile ;;
    *) echo "$audit audit will be run" ; auditRun $audit $role $profile ;;
  esac
fi

# button scripts
if [ -n "$button" ]; then
  case $action in
    ENABLE)   echo "$button will be enabled" ; buttonEnable $button $role $profile;;
    THEATER)  echo "$button will be simulated" ; buttonTheater $button $role $profile;;
  esac
fi