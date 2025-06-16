from setuptools import setup, find_packages

setup(
    name='swiftpredict',
    version='0.1.0',
    author='Manas Ranjan Jena',
    author_email='mranjanjena253@gmail.com',
    description='A lightweight AutoML and experiment tracking with custom logger, library with FastAPI backend and Python SDK. It works completely locally and just needs excess to your mongodb to log data.'
,
    long_description_content_type='text/markdown',
    url='https://github.com/ManasRanjanJena253/SwiftPredict',
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=[
        'fastapi',
        'uvicorn',
        'pymongo',
        'click',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'pandas',
        'numpy',
        'streamlit',
        'requests',
        'imbalanced-learn',  # correct PyPI name for imblearn
        'xgboost',
        'lightgbm',
        'scipy',
        'tqdm',
        "spacy"
    ],
    entry_points={
        'console_scripts': [
            'swiftpredict=swiftpredict.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
