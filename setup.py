from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='vega-slack',
    version='0.1.0',
    author='jinland',
    author_email='jinland67@gmail.com',
    description='Library for using Slack',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jinland67/vega-slack.git',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.10',
    install_requires=[
        'slack-sdk >= 3.13.0'
    ],
    package_data={"vega_slack": ["*.txt"]},
    include_package_data=True,
)