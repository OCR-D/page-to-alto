from setuptools import setup, find_packages

install_requires = open('requirements.txt').read().split('\n')

setup(
    name='ocrd-page-to-alto',
    version='0.0.1',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer',
    url='https://github.com/OCR-D/page-to-alto',
    license='Apache License 2.0',
    packages=find_packages(exclude=['tests', 'repo']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'page-to-alto=ocrd_page_to_alto.cli:main',
        ]
    },
)
