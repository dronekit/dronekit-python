from setuptools import setup, Extension
import numpy as np
import platform

version = '0.1.0'

ext_modules = []

setup (name = 'droneapi',
       zip_safe=True,
       version = version,
       description = 'Python language bindings for the DroneApi',
       long_description = '''Python language bindings for the DroneApi (includes the droneapi MAVProxy module)''',
       url = 'https://github.com/3drobotics/droneapi-python',
       author = '3D Robotics',
       install_requires = [ 'pymavlink',
                            'MAVProxy' ],
       author_email = 'kevinh@geeksville.com',
       classifiers=['Development Status :: 4 - Beta',
                    'Environment :: Console',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: Apache Software License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Scientific/Engineering'
                    ],
       license='apache',
       packages = ['droneapi', 'droneapi.module', 'droneapi.lib' ],
       ext_modules = ext_modules)
