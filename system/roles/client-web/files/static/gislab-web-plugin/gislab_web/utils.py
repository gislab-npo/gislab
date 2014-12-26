# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GIS.lab Web plugin
 Publish your projects into GIS.lab Web application
 ***************************************************************************/
"""

from decimal import Decimal


def to_decimal_array(value):
	"""Converts list of float/string numbers or comma-separated string to list of Decimal values"""
	if isinstance(value, basestring):
		return [Decimal(res_string.strip())for res_string in value.split(',')]
	else:
		return [Decimal(res) for res in value]

def scales_to_resolutions(scales, units, dpi=96):
	"""Helper function to compute tile resolutions from map scales."""

	dpi = Decimal(dpi)
	factor = {
		'feet': Decimal('12.0'), 'meters': Decimal('39.37'),
		'miles': Decimal('63360.0'), 'degrees': Decimal('4374754.0')
	}
	return [int(scale)/(dpi*factor[units]) for scale in scales]

def resolutions_to_scales(resolutions, units, dpi=96):
	"""Helper function to compute map scales from tile resolutions."""
	dpi = Decimal(dpi)
	factor = {
		'feet': Decimal('12.0'), 'meters': Decimal('39.37'),
		'miles': Decimal('63360.0'), 'degrees': Decimal('4374754.0')
	}
	return [int(round(resolution * dpi * factor[units])) for resolution in resolutions]
