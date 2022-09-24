from setuptools import setup

setup(name='cbpi4-SensorLogTarget-InfluxDB',
      version='0.0.1',
      description='CraftBeerPi4 Plugin to log sensor data to InfluxDB server or InfluxDB cloud',
      author='prash3r',
      author_email='pypi@prash3r.de',
      url='https://pypi.org/project/cbpi4-SensorLogTarget-InfluxDB/',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-SensorLogTarget-InfluxDB': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-SensorLogTarget-InfluxDB'],
     )