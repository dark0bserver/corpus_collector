from setuptools import setup

setup(
    name='corpus_collector',
    packages=['corpus_collector'],
    entry_points={
        "console_scripts": ['corpus_collector = corpus_collector.build_corpus_cli:main']
    },
    version='0.1',
    description = "Lexical corpus collector for domain page text extractions from Common Crawl.",
    author = "dark0bserver",
    url = "https://github.com/dark0bserver/corpus_collector",
    install_requires=[
        'requests',
        'boto3'
    ]
)