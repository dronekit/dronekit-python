from setuptools import setup, Extension
import platform

version = '1.0.2'

ext_modules = []

setup (name = 'droneapi',
       zip_safe=True,
       version = version,
       description = 'Python language bindings for the DroneApi',
       long_description = '''Python language bindings for the DroneApi (includes the droneapi MAVProxy module)''',
       url = 'https://github.com/diydrones/droneapi-python',
       author = '3D Robotics',
       install_requires = [ 'pymavlink',
                            'MAVProxy >= 1.3.13',
                            'protobuf >= 2.5.0' ],
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
       # doesn't work: package_data={'droneapi': ['example/*']},
       ext_modules = ext_modules)
