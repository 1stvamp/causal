__version__ = '0.9.2'

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
        name='causal',
        description='Open source lifestream aggregator',
        version=__version__,
        author='Project Causal Team',
        author_email='team@projectcausal.com',
        url='http://www.projectcausal.com/',
        download_url='https://github.com/causality/causal/tarball/%s' % (__version__,),
        keywords=['lifestream', 'aggregator', 'socialnetwork', 'django', 'social'],
        packages=find_packages('src', exclude=['ez_setup']),
        package_dir={'': 'src'},
        setup_requires=open('virtualenv_build/base_requirements.txt', 'r').readlines(),
        install_requires=['setuptools'],
        extras_require={
            'services': open('virtualenv_build/extras_requirements.txt', 'r').readlines(),
        },
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
