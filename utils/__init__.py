#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

version_number = {'major': 0, 'minor': 2}
version_string = 'CoatingGUI v{major}.{minor}'.format(**version_number)


def compare_versions(v1, v2):
    if v1['major'] > v2['major']:
        return 1
    elif v1['major'] < v2['major']:
        return -1
    else:
        if v1['minor'] > v2['minor']:
            return 1
        elif v1['minor'] < v2['minor']:
            return -1
        else:
            return 0

