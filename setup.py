from setuptools import setup, find_packages

setup(
	name="networkinterfaces",
	version="0.0.1",
	description="A module for dealing with network interfaces",
	author="Brandon Hammond",
	author_email="newdaynewburner@gmail.com",
	packages=find_packages(),
	install_requires=[
		"pywifi",
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: POSIX :: Linux",
	],
	python_requires=">=3.6",
)
