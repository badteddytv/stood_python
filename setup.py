from setuptools import setup

setup(name='stood',
        version='0.3',
        description='',
        url='http://github.com/badteddytv/stood_python',
        author='Neil Dwyer',
        author_email='neil@badteddy.tv',
        packages=['logger'],
        install_requires=[
            'aiohttp'
            ],
        tests_require=['pytest'],
        zip_safe=False)
