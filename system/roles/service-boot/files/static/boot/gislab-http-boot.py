from urlparse import parse_qs
import re

def application(environ, start_response):

    # read GIS.lab configuration
    CONFIG = {}
    with open('/etc/gislab_version', 'r') as f:
        param_pattern = re.compile('\s*(\w+)\s*\=\s*"([^"]*)"')
        for line in f:
            config = param_pattern.match(line)
            if config:
                k, v = config.groups()
                CONFIG[k] = v

    try:
        ip = parse_qs(environ['QUERY_STRING'])['ip'][0]
    except KeyError:
        ip = "{0}.5".format(CONFIG['GISLAB_NETWORK'])

    response = """#!ipxe
        kernel http://{0}/boot/vmlinuz ro root=/dev/nbd0 init=/sbin/init-gislab nbdroot=:10809/gislab
        initrd http://{0}/boot/initrd.img
        boot
    """.format(ip)
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(response)))]

    status = '200 OK'
    start_response(status, response_headers)
    return [response]

# vim: set ts=8 sts=4 sw=4 et:
