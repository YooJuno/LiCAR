from setuptools import find_packages, setup

package_name = 'turtlebot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/turtlebot_base.launch.py']),
        ('share/' + package_name + '/launch', ['launch/turtlebot_launch_test.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dain',
    maintainer_email='didek5123@naver.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtlebot_spawner = turtlebot_pkg.turtlebot_spawner:main',
            'turtlebot_mover = turtlebot_pkg.turtlebot_mover:main',
            'publicher = turtlebot_pkg.publicher:main'

        ],
    },
)
