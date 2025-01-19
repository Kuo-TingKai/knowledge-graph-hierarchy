from setuptools import setup, find_packages

setup(
    name="knowledge_graph_hierarchy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "SPARQLWrapper==2.0.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
    ],
)