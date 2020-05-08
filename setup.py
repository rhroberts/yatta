#!/usr/bin/env python
import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='yatta',
    version='0.0.1',
    description="Yet Another Time Tracking Tool",
    long_description=long_description,
    author='Rusty Roberts',
    author_email='rust.roberts@protonmail.com',
    url='https://github.com/rhroberts/yatta',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['click', 'pyfiglet'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 1 - Planning',
    ],
    py_modules=['yatta'],
    entry_points={
        'console_scripts': [
            "yatta=yatta:main"
        ]
    }
)
