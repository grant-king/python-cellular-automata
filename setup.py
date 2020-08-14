import setuptools

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="pythoncellularautomata",
    version="0.0.1",
    author="Grant King",
    author_email="grantryanking@gmail.com",
    description="Cellular Automaton simulator using Pygame."
    long_description=long_description,
    url="https://github.com/grant-king/python-cellular-automata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPL",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["pygame", "opencv-python", "numpy", "numba", "scikit-image"]

)