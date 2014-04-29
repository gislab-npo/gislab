#!/bin/bash
# Drop all incoming and outgoing DHCP requests.
# Useful for developer's machines.


for port in 67 68; do
	for chain in INPUT OUTPUT; do
		for proto in udp tcp; do
			for direction in sport dport; do
				iptables -A $chain -p $proto "--$direction" $port -j DROP;
			done;
		done;
	done;
done


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
