name, version = 'zc.twotieredkanban', '0'

install_requires = [
    'bobo',
    'gevent',
    'gevent-websocket',
    'requests',
    'setuptools',
    'zc.dojoform',
    'zc.recipe.deployment',
    'zc.recipe.rhrc',
    'zc.zdaemonrecipe',
    'zc.zk [static]',
    'zdaemon',
    ]
extras_require = dict(test=['manuel', 'mock', 'zope.testing'])

entry_points = """
[zc.buildout]
default = zc.asanakanban.akbrecipe:Recipe

[paste.server_runner]
main = zc.asanakanban.server:runner
"""

from setuptools import setup

long_description=open('README.rst').read()

setup(
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    license = 'ZPL 2.1',

    name = name, version = version,
    long_description = long_description,
    description = long_description.strip().split('\n')[1],
    packages = [name.split('.')[0], name],
    namespace_packages = [name.split('.')[0]],
    package_dir = {'': 'src'},
    install_requires = install_requires,
    zip_safe = False,
    entry_points=entry_points,
    package_data = {name: ['*.txt', '*.test', '*.html']},
    extras_require = extras_require,
    tests_require = extras_require['test'],
    test_suite = name+'.tests.test_suite',
    )
