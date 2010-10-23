try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
        name='causal',
        description='Open source lifestream aggregator',
        version='0.9',
<<<<<<< HEAD
        author='Chris Hannam',
        author_email='bassdread@gmail.com',
        url='http://github.com/bassdread/causal',
=======
        author='Project Causal Team',
        author_email='team@projectcausal.com',
        url='http://github.com/causality/causal',
>>>>>>> upstream/master
        packages=find_packages('src', exclude=['ez_setup']),
        package_dir={'': 'src'},
        setup_requires=open('virtualenv_build/base_requirements.txt', 'r').readlines(),
        install_requires = ['setuptools'],
        extras_require={
            'services': open('virtualenv_build/extras_requirements.txt', 'r').readlines(),
        },
        license='Apache License 2.0'
)
