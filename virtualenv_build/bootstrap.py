#!/usr/bin/env python
# bootstrap.py
# Bootstrap and setup a virtualenv with the specified requirements.txt
import os
import sys
import shutil
import subprocess
from optparse import OptionParser


usage = """usage: %prog [options]"""
parser = OptionParser(usage=usage)
parser.add_option("-c", "--clear", dest="clear", action="store_true",
                  help="clear out existing virtualenv")
parser.add_option("-b", "--base", dest="base", action="store_true",
                  help="only install base requirements")


def main():
    if "VIRTUAL_ENV" not in os.environ:
        sys.stderr.write("$VIRTUAL_ENV not found.\n\n")
        parser.print_usage()
        sys.exit(-1)
    (options, pos_args) = parser.parse_args()
    virtualenv = os.environ["VIRTUAL_ENV"]
    if options.clear:
        subprocess.call(["virtualenv", "--clear", "--distribute", virtualenv])
    file_path = os.path.dirname(__file__)
    print "Installing base requirements"
    subprocess.call(["pip", "install", "-E", virtualenv, "--requirement",
                     os.path.join(file_path, "../requirements.txt")])
    if not options.base:
        print "Installing extras requirements"
        subprocess.call(["pip", "install", "-E", virtualenv, "--requirement",
                        os.path.join(file_path, "../extras_requirements.txt")])

    # Try to add the parent into PYTHONPATH for the virtualenv
    parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    python_version = sys.version[:3]
    site_packages = "%s/lib/python%s/site-packages" % (virtualenv, python_version,)
    if os.path.exists(site_packages):
        path_file = "%s/virtualenv_path_extensions.pth" % (site_packages,)
        if os.path.exists(path_file):
            f = open(path_file, 'r+')
            paths = f.readlines()
            if "%s\n" % (parent_path,) not in paths:
                f.seek(0)
                f.write("%s\n%s" % (parent_path, "\n".join(paths),))
                print "Added '%s' to virtualenv PYTHONPATH" % (parent_path,)
            f.close()



if __name__ == "__main__":
    main()
    sys.exit(0)
