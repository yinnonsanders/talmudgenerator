from setuptools import setup

setup(
	name='talmudgenerator',
	packages=['talmudgenerator'],
	include_package_data=True,
	install_requires=[
		'flask',
		'flask_bootstrap',
		'keras',
	],
)
