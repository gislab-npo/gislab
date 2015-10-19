import re

GISLAB_INFO = {}
try:
	with open('/etc/gislab_version', 'r') as f:
		param_pattern = re.compile('\s*(\w+)\s*\=\s*"([^"]*)"')
		for line in f:
			match = param_pattern.match(line)
			if match:
				name, value = match.groups()
				GISLAB_INFO[name] = value
except IOError:
	pass

class GislabHeaderMiddleware(object):
	def process_response(self, request, response):
		version = GISLAB_INFO.get('GISLAB_VERSION', None)
		if version:
			response['Access-Control-Expose-Headers'] = 'X-GIS.lab-Version'
			response['X-GIS.lab-Version'] = version
		return response
