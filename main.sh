#!/bin/sh

# init by making scripts executable
chmod 755 Buttons/*.sh
chmod 755 Audit/*.sh
chmod 755 Theater/*.sh

# defaults -- provide them up here, and they can be used in the help printoutrepository= ~donaldp/
role=scimma_test_power_user

printHelp () {
cat - <<EOF
Security scripts for SCiMMA AWS
Options
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -b     button to toggle: RED, YELLOW or GREEN
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
            whoami - describes current user
EOF
}

buttonEnable () {
  case $1 in
    RED)    ./Buttons/depriv.sh -r $2 ; ./Buttons/ec2stop.sh ;;
    YELLOW) echo "yellow button not implemented yet" ;;
    GREEN)  ./Buttons/priv.sh $2 ;;
  esac
  echo "$1 button engaged"
}

buttonTheater () {
  case $1 in
    RED)    ./Theater/red.sh ; ./Theater/ec2fake.sh ;;
    YELLOW) echo "yellow button not implemented yet" ;;
    GREEN)  ./Theater/green.sh $2 ;;
  esac
  echo "$1 simulated"
}

auditRun () {
  case $1 in
    all) auditRun dependencies ; auditRun myprivileges ; auditRun policies $2 ; auditRun whoami ; auditRun repo  ;;
    dependencies) ./Audit/dependencies.sh ;;
    myprivileges) ./Audit/privileges.sh ;;
    policies) ./Audit/policies.sh -r $2 ;;
    whoami) ./Audit/whoami.sh ;;
    repo) git remote show origin ;;
  esac
  echo "$1 audit complete"
}

# option processing  $OPTARG fetches the argument
while getopts hxb:r:eta: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      b) button=$OPTARG ;;
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

#echo $button $*

# audit scripts
if [ -n "$audit" ]; then
  case $audit in
    all) echo "All audits will be run" ; auditRun all $role ;;
    policies) echo "$audit audit will be run" ; auditRun $audit $role ;;
    *) echo "$audit audit will be run" ; auditRun $audit ;;
  esac
fi

# button scripts
if [ -n "$button" ]; then
  case $action in
    ENABLE)   echo "$button will be enabled" ; buttonEnable $button $role ;;
    THEATER)  echo "$button will be simulated" ; buttonTheater $button ;;
  esac
fi