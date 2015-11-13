def reverse_ip(addr):
    """ Get reversed IP address. """

    a = addr.split(".")
    return "{2}.{1}.{0}".format(*a)

def cidr_block_from_network_16(addr):
    """ Get 16 bit CIDR from network number. """

    a = addr.split(".")
    return "{0}.{1}.0.0/16".format(*a)


class FilterModule(object):
    ''' utility filters for networking '''
    def filters(self):
        return {
            'reverse_ip' : reverse_ip,
            'cidr_block_from_network_16' : cidr_block_from_network_16
        }

# vim: set ts=8 sts=4 sw=4 et:
