# setup.py
from setuptools import setup, find_packages

setup(
    name='pipeline',
    version='0.1',
    packages=find_packages(),
    install_requires=[],  # Add any dependencies your library has
    entry_points={
        'pipeline.plugins': [],  # This allows for plugin discovery
    },
    include_package_data=True,
    license='MIT',
    description='A description of pipeline',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kibrq/pipeline',  # Replace with your GitHub URL
    author='Kirill Brilliantov',
    author_email='ki.br178@gmail.com',
)
