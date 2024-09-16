from setuptools import setup, find_packages
from json import load 

install_requires = open('requirements.txt').read().split('\n')
with open('./ocrd_page_to_alto/ocrd-tool.json', 'r', encoding='utf-8') as f:
    version = load(f)['version']

setup(
    name='ocrd-page-to-alto',
    version=version,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer, Robert Sachunsky',
    url='https://github.com/OCR-D/page-to-alto',
    license='Apache License 2.0',
    packages=find_packages(exclude=['tests', 'repo']),
    install_requires=install_requires,
    package_data={
        '': ['*.json']
    },
    entry_points={
        'console_scripts': [
            'page-to-alto=ocrd_page_to_alto.cli:main',
            'ocrd-page2alto-transform=ocrd_page_to_alto.ocrd_cli:main',
        ]
    },
)
