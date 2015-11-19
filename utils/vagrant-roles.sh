#!/bin/bash
# Run only specified GIS.lab roles.
# USAGE: vagrant-roles.sh <role-name>


PYTHONUNBUFFERED=1
ANSIBLE_FORCE_COLOR=true
ANSIBLE_HOST_KEY_CHECKING=false
ANSIBLE_SSH_ARGS='\
    -o UserKnownHostsFile=/dev/null \
    -o ForwardAgent=yes \
    -o ControlMaster=auto \
    -o ControlPersist=60s'

ansible-playbook \
  --private-key=$(pwd)/.vagrant/machines/gislab_vagrant/virtualbox/private_key \
  --user=vagrant \
  --connection=ssh \
  --limit='gislab_vagrant' \
  --inventory-file=$(pwd)/.vagrant/provisioners/ansible/inventory \
  --extra-vars='{"GISLAB_ADMIN_PASSWORD":"gislab","GISLAB_SERVER_NETWORK_DEVICE":"eth1"}' \
  --verbose \
  --tags installation-setup,$@ \
system/gislab.yml

# vim: set ts=8 sts=4 sw=4 et:
