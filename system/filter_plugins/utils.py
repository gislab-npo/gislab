import re

def split_string(string, seperator=' '):
    """ Split string on separator """
    return string.split(seperator)

def split_regex(string, seperator_pattern):
    """ Split string on regular expression """
    return re.split(seperator_pattern, string)


# Dedicated filters
def keyboard_layouts_filter(values):
    """ Return keyboards layout configuration as a string of comma separated layouts
    and variants separated by colon.
    """
    layouts = []
    variants = []
    for keyboard in values:
        layouts.append(keyboard['layout'])
        try:
            variants.append(keyboard['variant'])
        except KeyError:
            variants.append('')
    ret = (',').join(i for i in layouts)
    ret += ":"
    ret += (',').join(i for i in variants)
    return ret

def postgresql_shm(mem):
    """ Get recommended value of kernel shmmax configuration
    based on total server RAM for running PostgreSQL db.
    System shmmax value which must be something little bit higher
    than one fourth of system memory size.
    """

    return int(round(mem * 1000000 / 3.5))


class FilterModule(object):
    ''' utility filters '''
    def filters(self):
        return {
            'split_string': split_string,
            'split_regex': split_regex,
            'postgresql_shm': postgresql_shm,
            'keyboard_layouts_filter': keyboard_layouts_filter
        }


# vim: set ts=8 et sw=4 sts=4
