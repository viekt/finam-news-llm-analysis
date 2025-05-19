from setuptools import setup, find_packages

setup(
     name='finance_toolkit',
     version='0.1.0',
     package_dir={'': 'src'},
     packages=find_packages('src'),
     install_requires=[
         'pandas',
         'selenium',
         'requests',
         'moexalgo',
         'openpyxl',
         'python-dotenv',
         'openai',
         'backoff',
         'logging',
         'matplotlib',
         'seaborn',
         'scikit-learn',
         'pyfixest'
     ],
     entry_points={
         'console_scripts': [
             'news-parser=newsparser.cli:main',
             'chatgpt-news-label=chatgpt_news_label.cli:main',
             "market-load=market_data_loader.cli:main",
         ],
     },
 )

