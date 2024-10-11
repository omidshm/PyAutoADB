from setuptools import find_packages, setup

setup(
    name="PyAutoADB",
    version="0.1.0",
    author="Lunateek",
    author_email="omidsha@pm.me",
    description="PyAutoGUI but for Android",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/omidshm/PyAutoADB",  # Replace with your repository
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[],  # Add your package dependencies
)
