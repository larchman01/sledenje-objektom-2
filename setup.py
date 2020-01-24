from setuptools import setup

setup(
    name="sledenje-objektom-2",
    version="0.0.7",
    description="sledenje-objektom-2",
    url="git@github.com:RoboLiga/sledenje-objektom-2.git",
    author="Jakob Maležič",
    author_email="jakob.malezic@gmail.com",
    license="unlicense",
    packages=["sledilnik"],
    install_requires=[
        'opencv-contrib-python',
        'ujson',
        'numpy'
    ],
    zip_safe=False
)
