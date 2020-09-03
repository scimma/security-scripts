#!/bin/sh
# main script that launches all the others

# init by making scripts executable and updating the tool
chmod 755 bin/Buttons/*.sh
chmod 755 bin/Audit/*.sh
chmod 755 tests/*.sh
# git pull

# formatting vars
bold=$(tput bold)
normal=$(tput sgr0)

# defaults
role=scimma_power_user
profile=scimma-uiuc-aws-admin


printHelp () {
# help function
cat - <<EOF
${bold}NAME${normal}
   security-scripts - security scripts for SCiMMA AWS

${bold}SYNOPSIS${normal}
   ./main.sh [-b RED] [-e] ...
   ./main.sh [-a all] ...
   ./main.sh -h

${bold}DESCRIPTION${normal}
   security-scripts is a shell script bundle that allows rapidly
   suspending/reinstating AWS role access and stopping EC2 acti-
   vity, regardless of any association with the role being de-
   privileged. The bundle has self-assessment and dry run capa-
   bilities

${bold}OPTIONS${normal}
   SETTINGS:
   -h     print help and exit
   -x     debugme: turn on shell tracing (e.g. set -x)
   -p     AWS CLI profile to use (default: ${profile})
   -r     AWS role to apply the button to (default: ${role})
   -b     button to toggle:
            ${bold}RED${normal} deprivileges the role specified by -r parameter
              to be read-only and stops all EC2 instances in all regions star-
              ted by any user. The instances will shut down, but not terminated.
            ${bold}GREEN${normal} restores privileges to the role specified
              by -r parameter

   OPERATION:
   -e     enable the specified button
   -t     test mode "dry run" button engagement that simulates -e command

   AUDIT:
   -a     audit mode; available audits:
            all           run all audits
            dependencies  checks for dependencies installed
            myprivileges  checks if current CLI user has sufficient privileges
            policies      checks what policies the target AWS role has
            repo          checks if repo is up to date and consistency
            roles         lists all IAM roles and their descriptions
            whoami        describes current user

${bold}AUTHOR${normal}
   Vladislav Ekimtcov (https://github.com/VladislavEkimtcov/)
EOF
}

buttonConfirmation () {
# Yes/No to engage button or quit
  read -p "Engage $1 button? [y/n] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
      echo "$1 button aborted"
      exit 1
  fi
}

buttonEnable () {
# button engagement function
  case $1 in
    RED) buttonConfirmation $1; ./bin/Buttons/depriv.sh -r $2 -p $3; ./bin/Buttons/ec2stop.sh -p $3 ;;
    # YELLOW) echo "yellow button not implemented yet" ;;
    GREEN) buttonConfirmation $1; ./bin/Buttons/priv.sh -r $2 -p $3 ;;
  esac
  echo "$1 button engaged"
}

buttonTest () {
# button simulation function
  case $1 in
    RED) buttonConfirmation $1; ./tests/red.sh -r $2 -p $3; ./tests/ec2fake.sh -p $3 ;;
    # YELLOW) echo "yellow button not implemented yet" ;;
    GREEN) buttonConfirmation $1; ./tests/green.sh -r $2 -p $3 ;;
  esac
  echo "$1 simulated"
}

auditRun () {
  case $1 in
    all) auditRun dependencies; auditRun myprivileges $2 $3; auditRun policies $2 $3;
      auditRun repo $2 $3; auditRun roles $2 $3; auditRun whoami $2 $3; ;;
    dependencies) ./bin/Audit/dependencies.sh ;;
    myprivileges) ./bin/Audit/privileges.sh -p $3 ;;
    policies) ./bin/Audit/policies.sh -r $2 -p $3 ;;
    whoami) ./bin/Audit/whoami.sh -p $3 ;;
    roles) ./bin/Audit/roles.sh -p $3 ;;
    repo) git remote show origin ;;
  esac
  echo "$1 audit complete"
  echo "_________________"
}

# option processing, $OPTARG fetches the argument
while getopts hxb:p:r:eta: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      b) button=$OPTARG ;;
      p) profile=$OPTARG ;;
      r) role=$OPTARG ;;
      e) action=ENABLE ;;
      t) action=TEST ;;
      a) audit=$OPTARG ;;
      *) printHelp; exit 1 ;;
  esac;
done
if [ $OPTIND -eq 1 ]; then printHelp ; exit 0; fi

#get rid of processed  options $* is now arguements.
shift `expr $OPTIND - 1`


# audit script selection
if [ -n "$audit" ]; then
  case $audit in
    all) echo "All audits will be run"; auditRun all $role $profile ;;
    policies) echo "$audit audit will be run"; auditRun $audit $role $profile ;;
    *) echo "$audit audit will be run"; auditRun $audit $role $profile ;;
  esac
fi

# button script selection logic
if [ -n "$button" ]; then
  case $action in
    ENABLE) echo "$button will be enabled"; buttonEnable $button $role $profile ;;
    TEST) echo "$button will be simulated"; buttonTest $button $role $profile ;;
  esac
fi