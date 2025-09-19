from setuptools import find_packages, setup
import glob
import os

package_name = 'turtlebot_pkg'

config_files = glob.glob(os.path.join('config', '*'))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', config_files),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dain',
    maintainer_email='didek5123@naver.com',
    description='Turtlebot mover package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtlebot_mover = turtlebot_pkg.turtlebot_mover:main',
            'main = turtlebot_pkg.main:main',
            'main_test = turtlebot_pkg.main_test:main',
        ],
    },
)
