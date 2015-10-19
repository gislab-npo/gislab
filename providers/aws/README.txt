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


8. Get the PV-GRUB AKI with ami-tools:

    $ AKI=$(ec2-describe-images -o amazon --filter "name=pv-grub-hd0_*.gz" \
                          --show-empty-fields --hide-tags \
                          --region <region> --filter "architecture=<client-architecture>" | \
      head -1 | awk '{ print $2 }')

   where <region> is region where GIS.lab server is running and <clien-architecture>
   is i386 for 32-bit GIS.lab clients or x86_64 for 64-bit GIS.lab clients.


8. Register GIS.lab client AMI with ami-tools:

    $ ec2-register <GISLAB_AWS_BUCKET_PREFIX>/<GISLAB_UNIQUE_ID>/gislab-aws-client.manifest.xml \
                   --name "gislab-aws-client-<GISLAB_UNIQUE_ID>" \
                   --description "GIS.lab AWS client AMI - <GISLAB_UNIQUE_ID>" \
                   --architecture <client-architecture> \
                   --virtualization-type paravirtual \
                   --kernel $AKI

   where <clien-architecture> is i386 for 32-bit GIS.lab clients or x86_64 for 64-bit GIS.lab clients.


9. In AWS console launch GIS.lab clients with these settings:

    - AMI - AMI which you get in previous step
    - EC2 instance type[1]
    - Network - "GIS.lab (ID: <GISLAB_UNIQUE_ID>)"
    - Subnet - "GIS.lab (ID: <GISLAB_UNIQUE_ID>)"
    - Auto-assign Public IP - Use subnet setting (Disable)
    - Security Group - "GIS.lab (ID: <GISLAB_UNIQUE_ID>)"
    - AWS SSH key pair - "GIS.lab (ID: <GISLAB_UNIQUE_ID>)"
    - Tags:
      * Name="GIS.lab client (ID: <GISLAB_UNIQUE_ID>)"
      * GISLAB_UNIQUE_ID="<GISLAB_UNIQUE_ID>"


   [1] - For production deployment 'm1.small' type should be enough. For more informations
         about instance types see http://aws.amazon.com/ec2/instance-types/.
         Supported instance types according to client architecture:
           * i386: m1.small, m1.medium, c1.medium, c3.large
           * amd64: all types of m1, m2, m3, c1, c3

