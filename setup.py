"""Install the script."""

from setuptools import setup
try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md', 'r').read()


setup(
    name="meshify",
    version='0.2.1',
    description='Package to interact with the Meshify API',
    long_description=description,
    long_description_content_type='text/x-rst',
    py_modules=['meshify'],
    license="Apache 2.0",
    author='Patrick McDonagh',
    author_email='patrickjmcd@gmail.com',
    url='https://patrickjmcd.github.io/Meshify-Python-API/',
    install_requires=[
        'Click',
        'requests'
    ],
    keywords='meshify api cloud',
    project_urls={
        'Source': 'https://github.com/patrickjmcd/Meshify-Python-API/',
        'Tracker': 'https://github.com/patrickjmcd/Meshify-Python-API/issues',
    },
    entry_points='''
        [console_scripts]
        meshify=meshify:cli
        ''',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
