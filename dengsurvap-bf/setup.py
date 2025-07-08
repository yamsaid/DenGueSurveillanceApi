try:
    from setuptools import setup, find_packages
except ImportError:
    # Fallback for environments without setuptools
    import os
    
    def setup(**kwargs):
        """Dummy setup function"""
        print("Warning: setuptools not available. Please install setuptools to build the package.")
        return None
    
    def find_packages(where='.', exclude=()):
        """Simple package finder"""
        packages = []
        for root, dirs, files in os.walk(where):
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if any(exclude_pattern in root for exclude_pattern in exclude):
                continue
            if '__init__.py' in files:
                packages.append(root.replace('/', '.').replace('\\', '.'))
        return packages

import os

# Lire le README pour la description longue
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Client Python pour l'API de surveillance de la dengue"

# Lire les exigences depuis requirements.txt
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

setup(
    name="dengsurvap-bf",
    version="0.1.0",
    author="Saïdou YAMEOGO - Data Analyst",
    author_email="saidouyameogo3@gmail.com",
    description="Client Python pour l'API de surveillance de la dengue ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yamsaid/dengsurvap-bf",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
        "openpyxl>=3.0.0",
        "PyJWT>=2.0.0",
        "cryptography>=3.0.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "analysis": [
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dab=dengsurvab.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dengsurvab": ["*.json", "*.yaml", "*.yml"],
    },
    keywords="dengue, epidemiology, surveillance, health, api, client",
    project_urls={
        "Bug Reports": "https://github.com/yamsaid/dengsurvap-bf/issues",
        "Source": "https://github.com/yamsaid/dengsurvap-bf",
        "Documentation": "https://dengsurvap-bf.readthedocs.io/",
    },
) 