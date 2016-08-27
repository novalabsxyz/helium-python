from setuptools import setup, find_packages

author = 'Marc Nijdam'
author_email = ''
packages = ['helium']
requires = [
    "future>=0.15",
    "requests<2.11",
    "uritemplate>=0.6",
    "inflection>=0.3",
]
setup_requires = ['vcversioner']
setup(
    name='helium-python',
    description='Wrapper for the Helium API',
    long_description="Python toolkit for working with the Helium API",
    author=author,
    author_email=author_email,
    url='https://github.com/helium/helium-python',
    packages=packages,
    setup_requires=setup_requires,
    install_requires=requires,
    include_package_data=True,
    license='BSD',
    vcversioner={"version_module_paths" : ["helium/_version.py"]},
)
