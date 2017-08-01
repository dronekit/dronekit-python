from setuptools import setup, Extension
import platform

version = '2.9.1'

setup(name='dronekit',
      zip_safe=True,
      version=version,
      description='Developer Tools for Drones.',
      long_description='Python API for communication and control of drones over MAVLink.',
      url='https://github.com/dronekit/dronekit-python',
      author='3D Robotics',
      install_requires=[
          'pymavlink>=2.2.3',
          'monotonic==1.2',
          'future==0.15.2'
      ],
      author_email='tim@3drobotics.com, kevinh@geeksville.com',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering',
      ],
      license='apache',
      packages=[
          'dronekit', 'dronekit.test'
      ],
      ext_modules=[])
