from setuptools import setup, find_packages

setup(
    name='swiftpredict',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'fastapi', 'uvicorn', 'pymongo', 'click', 'scikit-learn', 'matplotlib', 'seaborn', 'pandas', 'numpy'
    ],
    entry_points={
        'console_scripts': [
            'swiftpredict=cli:cli',
        ],
    },
)
