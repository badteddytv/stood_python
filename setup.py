from setuptools import setup, find_packages

setup(name='stood',
        version='0.4',
        description='',
        url='http://github.com/badteddytv/stood_python',
        author='Neil Dwyer',
        author_email='neil@badteddy.tv',
        packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        install_requires=[
            'aiohttp'
            ],
        tests_require=['pytest'],
        zip_safe=False)
