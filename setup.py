import setuptools

import sexmachine

setuptools.setup(
    name='sexmachine',
    version=sexmachine.__version__,
    author='Jon Reades',
    author_email='jon@reades.com',
    packages=['sexmachine', 'sexmachine.test'],
    package_dir={'sexmachine': 'sexmachine'},
    package_data={'sexmachine': ['data/*.txt.gz']},
    url='https://github.com/jreades/sexmachine',
    license='GPLv3',
    description='Infer the gender from first name using data from gender.c library.',
    long_description=open('README.rst','r').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
