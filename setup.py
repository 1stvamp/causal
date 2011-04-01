import os

cwd = os.path.dirname(__file__)
__version__ = open(os.path.join(cwd, 'src', 'causal', 'version.txt'), 'r').read().strip()

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

def parse_requires(path):
    reqs = []
    links = []
    for req in open(path, 'r').readlines():
        link = None
        if '://' and '#' in req:
            link, req = req.split('#')
        reqs.append(req)
        if link:
            links.append(link)
    return reqs, links

setup_requires, dependency_links = parse_requires(os.path.join(cwd, 'requirements.txt'))
extras_requires, dependency_links2 = parse_requires(os.path.join(cwd, 'extras_requirements.txt'))
dependency_links.extend(dependency_links2)

print dependency_links

setup(
        name='causal',
        description='Open source lifestream aggregator',
        version=__version__,
        author='Project Causal Team',
        author_email='team@projectcausal.com',
        url='http://www.projectcausal.com/',
        download_url='https://github.com/causality/causal/tarball/%s' % (__version__,),
        keywords=['lifestream', 'aggregator', 'socialnetwork', 'django', 'social'],
        packages=find_packages(os.path.join(cwd, 'src'), exclude=['ez_setup']),
        package_dir={'': os.path.join(cwd, 'src')},
        setup_requires=setup_requires,
        install_requires=['setuptools'],
        extras_require={
            'services': extras_requires,
        },
        dependency_links=dependency_links,
        license='Apache License 2.0',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Internet :: WWW/HTTP',
        ],
)
