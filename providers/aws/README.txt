---------------------------------------
- Launch GIS.lab server in Amazon EC2 -
---------------------------------------

1. Create appropriate configuration file 'system/host_vars/<GISLAB_UNIQUE_ID>'


2. Run ansible playbook which launch EC2 instance

    $ ansible-playbook --inventory 'localhost,' --extra-vars "GISLAB_UNIQUE_ID=<GISLAB_UNIQUE_ID>" providers/aws/aws.yml


3. In AWS console (or with ami-tools) create DHCP Options Sets:

    - Name tag: "GIS.lab (ID: <GISLAB_UNIQUE_ID>)"
    - Domain name servers: "<GISLAB_NETWORK>.5, <GISLAB_NETWORK>.2"

   Other options leave empty.


4. In AWS console (or with ami-tools) attach DHCP Options Sets "GIS.lab (ID: <GISLAB_UNIQUE_ID>)"
   to VPC "GIS.lab (ID: <GISLAB_UNIQUE_ID>)".


5. Reboot EC2 instance.


6. Add a host record with server name '<GISLAB_UNIQUE_ID>' in to inventory file
   to use your host variable file.

   Inventory file syntax:

    <GISLAB_UNIQUE_ID> ansible_ssh_host=<EC2-instance-URL> ansible_ssh_user=ubuntu


7. Install GIS.lab server to EC2 instance:

    $ ansible-playbook --inventory=inventory system/gislab.yml


8. Launch GIS.lab AWS clients:

    $ ansible-playbook --inventory=inventory --extra-vars "GISLAB_UNIQUE_ID=<GISLAB_UNIQUE_ID>" providers/aws/client.yml

