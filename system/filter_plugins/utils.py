import re

def split_string(string, seperator=' '):
    """ Split string on separator """
    return string.split(seperator)

def split_regex(string, seperator_pattern):
    """ Split string on regular expression """
    return re.split(seperator_pattern, string)

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
            'postgresql_shm': postgresql_shm
        }


# vim: set ts=8 et sw=4 sts=4
