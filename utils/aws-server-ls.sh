#!/bin/bash
# List all AWS GIS.lab server instances.


ec2-describe-instances --filter "tag:Name=GIS.lab server"

# vim: set ts=8 sts=4 sw=4 et:
