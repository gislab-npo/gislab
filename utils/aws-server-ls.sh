#!/bin/bash
# List AWS GIS.lab server instances.
# Author: Ivan Mincik, ivan.mincik@gmail.com


ec2-describe-instances --filter "tag:Name=GIS.lab server"

# vim: set ts=4 sts=4 sw=4 noet:
