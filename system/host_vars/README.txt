Directory for host specific GIS.lab configuration.
File names created here must match 'unique-host-name' specified in Ansible inventory file.

If using local Vagrant provisioner, create file with name 'gislab_vagrant' here. It will be automatically loaded by
Vagrant without need to manually create the inventory file.

Ansible inventory file format:
<unique-host-name> ansible_ssh_host=<host-url> ansible_ssh_user=<provisioning-user-account-name>
