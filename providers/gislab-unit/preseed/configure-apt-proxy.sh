#!/bin/sh

# This is a debconf-compatible script
. /usr/share/debconf/confmodule

# Create the template file
cat << EOF > /tmp/configure-apt-proxy.template
Template: configure-apt-proxy/ask
Type: string
Description: Enter the Apt proxy server address in standard form of "http://[[user[:pass]@]host[:port]/" or leave if blank for none.

Template: configure-apt-proxy/title
Type: text
Description: Configure Apt proxy server
EOF

# Load template
debconf-loadtemplate configure-apt-proxy /tmp/configure-apt-proxy.template

# Set title for dialog box
db_settitle configure-apt-proxy/title

# Ask it
db_input critical configure-apt-proxy/ask
db_go

# Get the answer
db_get configure-apt-proxy/ask

cat << EOF > /tmp/debconf-configure-apt-proxy.conf
d-i mirror/http/proxy string $RET
EOF

debconf-set-selections /tmp/debconf-configure-apt-proxy.conf
