from setuptools import setup

setup(
  name='vban_cmd',
  version='0.0.1',
  description='VBAN CMD Python API',
  packages=['vban_cmd'],
  install_requires=[
  ],
  extras_require={
    'development': [
      'nose',
      'randomize',
      'parameterized'
    ]
  }
)