#!/bin/sh

# init by making scripts executable
chmod 755 RedButton/*.sh

# defaults -- provide them up here, and they can be used in the help printoutrepository= ~donaldp/
role=scimma_test_power_user

printHelp () {
cat - <<EOF
run a program in various modes
    ./debug.sh program
Options
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -b     button to toggle: RED, YELLOW or GREEN
   -r     role to apply the button to (default: ${role})
   -e     enable the specified button
   -t     test mode "dry run" button engagement that simulates -e command
   -a     audit mode
            possible audits:
            dependencies - checks for dependencies installed
            privileges - checks if AWS CLI user has sufficient privileges

EOF
}

buttonEnable () {
  case $1 in
    RED)    ./RedButton/depriv.sh -r $2 ; ./RedButton/ec2stop.sh ;;
    YELLOW) echo "yellow button not implemented yet" ;;
    GREEN)  ./RedButton/priv.sh $2 ;;
  esac
  echo "$1 button engaged"
}

buttonTheater () {
  echo "$1 simulated"
}

# option processing  $OPTARG fetches the argument
while getopts hxb:eta: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      b) button=$OPTARG ;;
      r) role=$OPTARG ;;
      e) action=ENABLE ;;
      t) action=THEATER ;;
      a) audit=$OPTARG ;;
      $\*?) printHelp; exit 1 ;;
  esac;
done

#get rid of processed  options $* is now arguements.
shift `expr $OPTIND - 1`

#echo $button $*

# button on scripts
if [ -n "$button" ]; then
  case $action in
    ENABLE)   echo "$button will be enabled" ; buttonEnable $button $role ;;
    THEATER)  echo "$button will be simulated" ;;
  esac
fi