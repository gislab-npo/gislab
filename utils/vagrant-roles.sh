#!/bin/bash

### USAGE
function usage() {
    echo "USAGE: $(basename $0) [OPTIONS] <role-name>,<role-name>,..."
    echo "Run requested GIS.lab roles only."
    echo -e "\nOPTIONS
    -t run only tests for requested roles (useful for tests development)
    -h display this help
    "
    exit 255
}


### OPTIONS
opt_tests_only="no"

while getopts "t" OPTION
do
        case "$OPTION" in
            t) opt_tests_only="yes" ;;
            h) usage ;;
            \?) exit 1;;
        esac
done
shift $(($OPTIND - 1))

ROLES=$1


### VARIABLES
ansible_cmd="ansible-playbook \
  --private-key=$(pwd)/.vagrant/machines/gislab_vagrant/virtualbox/private_key \
  --user=vagrant \
  --connection=ssh \
  --limit=gislab_vagrant \
  --inventory-file=$(pwd)/.vagrant/provisioners/ansible/inventory \
  --extra-vars={\"GISLAB_ADMIN_PASSWORD\":\"gislab\",\"GISLAB_SERVER_NETWORK_DEVICE\":\"eth1\"} \
  --verbose"

if [ "$ROLES" != "" ]; then
    tags="--tags installation-setup,$ROLES,installation-done"
else
    tags=""
fi


### MAIN SCRIPT
PYTHONUNBUFFERED=1
ANSIBLE_FORCE_COLOR=true
ANSIBLE_HOST_KEY_CHECKING=false
ANSIBLE_SSH_ARGS='\
    -o UserKnownHostsFile=/dev/null \
    -o ForwardAgent=yes \
    -o ControlMaster=auto \
    -o ControlPersist=60s'

# run roles
if [ "$opt_tests_only" == "no" ]; then
    $ansible_cmd $tags system/gislab.yml
fi

# run tests for roles
$ansible_cmd $tags system/test.yml

# vim: set ts=8 sts=4 sw=4 et:
