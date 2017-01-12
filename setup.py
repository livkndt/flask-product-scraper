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
        'flask',
    ],
)
