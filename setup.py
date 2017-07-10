from setuptools import setup, find_packages

setup(
    name='netmon',
    version='1.5',

    description='Network Monitor',
    long_description='Network Monitor',
    url='https://github.com/bullerian/netmon',
    author='Stepan Dmuyro Myron Sasha Mykola',
    py_modules=['netmon', 'ping'],
    install_requires=['scapy-python3'],
    entry_points={
        'console_scripts': [
            'netmon=netmon:main',
        ]
    }
)