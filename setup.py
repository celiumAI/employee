from setuptools import setup, find_packages

setup(
    name='employee',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'employee=employee.main:cli',
        ],
    },
    install_requires=[
        'fire',
    ],
    author='Martin Christoph Frank',
    author_email='martinchristophfrank@gmail.com',
    description='does some work.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://localhost:8080/mcfrank/employee'
)

