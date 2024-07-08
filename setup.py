from setuptools import setup, find_packages

setup(
    name='Naive Novel Writer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # 依赖项
        'django>=3.2',
        'gunicorn',
    ],
   author='Haotian Xu'
)