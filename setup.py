import setuptools
import os

version = '2.9.2'

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    LongDescription = f.read()

setuptools.setup(
    name='dronekit',
    zip_safe=True,
    version=version,
    description='Developer Tools for Drones.',
    long_description_content_type="text/markdown",
    long_description=LongDescription,
    url='https://github.com/dronekit/dronekit-python',
    author='3D Robotics',
    install_requires=[
        'pymavlink>=2.2.20',
        'monotonic>=1.3',
    ],
    author_email='tim@3drobotics.com, kevinh@geeksville.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],
    license='apache',
    packages=setuptools.find_packages()
)
