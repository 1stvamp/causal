#!/usr/bin/env python
import os
import textwrap
import virtualenv

locn = os.path.dirname(os.path.realpath(__file__))

basereqs = open('base_requirements.txt', 'r')
reqs = open('requirements.txt', 'w')

for line in basereqs:
    if line.startswith('dependencies'):
        reqs.write("%s/%s" % (locn, line))
    else:
        reqs.write(line)

basereqs.close()
reqs.close()

script = virtualenv.create_bootstrap_script(textwrap.dedent("""
import os
import subprocess

def after_install(options, home_dir):
    subprocess.call([join(home_dir, 'bin', 'easy_install'), '-Z', '-f', '%(locn)s/dependencies/setuptools-0.6c11.tar.gz', 'setuptools'])
    subprocess.call([join(home_dir, 'bin', 'easy_install'), '-Z', '-f',
                                                            '%(locn)s/dependencies/pip-0.8.tar.gz',
                                                            'pip==0.8'])
    subprocess.call([join(home_dir, 'bin', 'pip'), 'install', '-r', '%(locn)s/requirements.txt'])
""" % {'locn':locn,}))
f = open('bootstrap.py', 'w').write(script)
