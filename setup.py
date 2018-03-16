from setuptools import setup

setup(
    name="meshify",
    version='0.1',
    py_modules=['meshify'],
    install_requires=[
        'Click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        meshify=meshify:cli
        ''',
)
