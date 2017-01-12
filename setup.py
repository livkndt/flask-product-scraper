from setuptools import setup, find_packages

setup(
    name='ProductScraperFlask',
    version='0.1',
    description='Python/Flask web scraper and microservice for processing products/categories.',
    author='Olivia Graham',
    author_email='livgrhm@gmail.com',
    platforms=['any'],
    license='MIT',
    packages = find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==0.12',
        'beautifulsoup4==4.5.3',
        'click==6.7',
        'itsdangerous==0.24',
        'Jinja2==2.9.4',
        'MarkupSafe==0.23',
        'ProductScraperFlask==0.1',
        'ruamel.ordereddict==0.4.9',
        'typing==3.5.3.0',
        'Werkzeug==0.11.15'
    ],
)
