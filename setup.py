from setuptools import setup

author = 'Helium'
author_email = 'hello@helium.com'
packages = ['helium']
requires = [
    "future>=0.15",
    "requests<2.11",
    "uritemplate>=0.6",
    "inflection>=0.3",
]
setup_requires = [
    'vcversioner',
]
with open('README.md', 'r') as infile:
    long_description = infile.read()

setup(
    name='helium-python',
    description='Wrapper for the Helium API',
    long_description=long_description,
    author=author,
    author_email=author_email,
    url='https://github.com/helium/helium-python',
    packages=packages,
    setup_requires=setup_requires,
    install_requires=requires,
    include_package_data=True,
    license='BSD',
    vcversioner={
        "version_module_paths": ["helium/_version.py"]
    },
)
