from setuptools import setup
setup(
	name='sfss',
	packages=['sfss'],
	include_package_data=True,
	install_requires=['sfss',
			'flask',
			'dnspython',
			'validate-email',
			'PyMySQL',
			'redis'],
	version='0.1',
	description='A simple way to share ABs on hosted systems',
	license='MIT',
	author='snake-whisper',
	author_email='snake-whisper@web-utils.ml',
	)
