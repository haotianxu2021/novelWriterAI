from setuptools import setup, find_packages

setup(
    name='Novel Writer',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=3.2',
        'gunicorn',
    ],
   author='Haotian Xu'
)