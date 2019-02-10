from distutils.core import setup

setup(
    name='SexMachine',
    version='0.1.2',
    author='Jon Reades',
    author_email='jon@reades.com',
    packages=['sexmachine', 'sexmachine.test'],
    package_dir={'sexmachine': 'sexmachine'},
    package_data={'sexmachine': ['data/*.txt.gz']},
    url='https://github.com/ferhatelmas/sexmachine/',
    license='GPLv3',
    description='Get the gender from first name.',
    long_description=open('README.rst').read(),
)
