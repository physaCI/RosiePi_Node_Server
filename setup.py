from setuptools import find_packages, setup

setup(
    name='rosiepi_node_server',
    version='0.0.1',
    packages=find_packages('node_server'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'jinja2',
        'rq',
        'redis'
    ]
)
