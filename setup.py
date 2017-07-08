from setuptools import setup, find_packages

setup(
    name='netmon',
    version='0.1.0',

    description='Network Monitor',
    long_description='Network Monitor',
    url='https://github.com/bullerian/netmon',
    author='TC6 command',
    py_modules=['netmon', 'ping'],
    install_requires=['scapy-python3'],
    entry_points={
        'console_scripts': [
            'netmon=netmon:main',
        ]
    }
)