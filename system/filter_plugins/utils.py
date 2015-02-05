import re

def split_string(string, seperator=' '):
    """ Split string on separator """
    return string.split(seperator)

def split_regex(string, seperator_pattern):
    """ Split string on regular expression """
    return re.split(seperator_pattern, string)


# Dedicated filters
def keyboard_layouts(keyboards, f=None):
    """ Return keyboards layout configuration as a string of comma separated layouts
    and variants separated by colon or only as comma separated layouts or variants if
    'f' (filter) is set. US keyboard is always available.
    """
    layouts = ['us',]
    variants = ['',]
    for keyboard in keyboards:
        layouts.append(keyboard['layout'])
        try:
            variants.append(keyboard['variant'])
        except KeyError:
            variants.append('')

    if not f:
        ret = (',').join(i for i in layouts)
        ret += ":"
        ret += (',').join(i for i in variants)
    elif f == 'layouts':
        ret = (',').join(i for i in layouts)
    elif f == 'variants':
        ret = (',').join(i for i in variants)

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
            'keyboard_layouts': keyboard_layouts
        }


# vim: set ts=8 et sw=4 sts=4
