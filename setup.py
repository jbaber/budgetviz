import setuptools

setuptools.setup(name='budgetviz',
  version='0.1',
  author='John Baber',
  author_email='budgetviz@frundle.com',
  packages=['budgetviz'],
  entry_points = {
    'console_scripts': ['budgetviz=budgetviz.command_line:main'],
  },
  install_requires=[
    'sqlalchemy',
    'yaml',
    'webbrowser',
    'docopt',
  ],
)
