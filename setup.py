from setuptools import setup, Extension
import platform

version = '2.1.0b1'

setup(name='dronekit',
      zip_safe=True,
      version=version,
      description='Python language bindings for the DroneApi',
      long_description='Python language bindings for the DroneApi',
      url='https://github.com/dronekit/dronekit-python',
      author='3D Robotics',
      install_requires=[
          'pymavlink>=1.1.62',
          'requests>=2.5.0,<=2.99999',
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
          'dronekit', 'dronekit.cloud', 'dronekit.test'
      ],
      ext_modules=[])
