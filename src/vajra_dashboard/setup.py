from setuptools import setup

package_name = 'vajra_dashboard'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vajra',
    maintainer_email='vajra@example.com',
    description='VAJRA mine rescue rover receiver dashboard',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'dashboard = vajra_dashboard.dashboard:main',
        ],
    },
)
