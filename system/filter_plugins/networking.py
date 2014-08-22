def reverse_ip(addr):
    """ Get reversed IP address. """

    a = addr.split(".")
    return "{2}.{1}.{0}".format(*a)


class FilterModule(object):
    ''' utility filters for networking '''
    def filters(self):
        return {
            'reverse_ip' : reverse_ip
        }


# vim: set ts=8 et sw=4 sts=4
