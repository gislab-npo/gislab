Directory for host specific GIS.lab configuration.
File names created here must match GIS.lab unique ID (unique host name) specified in Ansible inventory file.

If using local Vagrant provisioner, create file with name 'gislab_vagrant' here. It will be automatically loaded by
Vagrant without need to manually create the inventory file.

Ansible inventory file format:
<GIS.lab unique ID> ansible_ssh_host=<server-IP-address> ansible_ssh_user=<provisioning-user-name>
