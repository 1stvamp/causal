try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
        name='helios',
        description='Open source lifestream aggregator'
        version='0.2',
        author='Chris Hannam',
        author_email='bassdread@gmail.com',
        url='http://github.com/bassdread/helios',
        ackages=find_packages(exclude=['ez_setup']),
        setup_requires=open('virtualenv_build/base_requirements.txt', 'r').readlines(),
        extras_require={
            'services': open('virtualenv_build/extras_requirements.txt', 'r').readlines(),
        }
        #license='Apache License 2.0'
)
