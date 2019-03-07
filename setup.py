from setuptools import setup, find_packages

setup(name='stood',
        version='1.1',
        description='',
        url='http://github.com/badteddytv/stood_python',
        author='Neil Dwyer',
        author_email='neil@badteddy.tv',
        packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        tests_require=['pytest'],
        install_requires=['elasticsearch'],
        zip_safe=False)
