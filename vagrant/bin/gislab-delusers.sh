#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com


# remove lab users accounts
for i in {1..24}
do
	deluser --remove-home gislab$i
done


# vim: set ts=4 sts=4 sw=4 noet:
