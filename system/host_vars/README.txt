Directory for host specific GIS.lab configuration.
File names created here must match GIS.lab unique ID (GISLAB_UNIQUE_ID) specified in Ansible inventory file. Each
configuration file must contain GISLAB_UNIQUE_ID configuration, which must equal to the file name.

If using local Vagrant provisioner, create 'gislab_vagrant' configuration file here. It will be automatically loaded by
Vagrant without needing to create the inventory file.

Ansible inventory file format:
<GISLAB_UNIQUE_ID> ansible_ssh_host=<server-IP-address> ansible_ssh_user=<provisioning-user-name>
