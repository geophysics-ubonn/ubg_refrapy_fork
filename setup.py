#!/usr/bin/env python
from setuptools import setup
import os
import glob

scripts = glob.glob('src/*.py')

version_long = '0.1.0'

# generate entry points
entry_points = {'console_scripts': []}
scripts = [os.path.basename(script)[0:-3] for script in glob.glob('src/*.py')]
for script in scripts:
    print(script)
    entry_points['console_scripts'].append(
        '{0} = {0}:main'.format(script)
    )

# package data
os.chdir('lib/refrapy')
package_data = glob.glob('images/*')
os.chdir('../../')


if __name__ == '__main__':
    setup(
        name='ubg_refrapy_fork',
        version=version_long,
        description='Refrapy fork of University of Bonn, Section Geophysics',
        author='Maximilian Weigand',
        license='MIT',
        author_email='mweigand@geo.uni-bonn.de',
        url='https://github.com/geophysics-ubonn/ubg_refrapy_fork',
        entry_points=entry_points,
        # python_requires='>=3.11',
        # entry_points={
        #     'console_scripts': [
        #         'td_test = td_test:main',
        #     ],
        # },
        # package_dir={'': 'src/', 'crtomo': 'lib/crtomo'},
        package_dir={
            '': 'src',
            'refrapy': 'lib/refrapy',
        },
        # packages=[''],
        # package_dir={'': 'lib', 'grid_tools': 'src/GRID_TOOLS'},
        # packages=find_packages(),
        # packages=['crtomo', 'crtomo.notebook', ],
        packages=['refrapy', ],
        package_data={'refrapy': package_data},
        py_modules=scripts,
        install_requires=[
            'importlib_resources',
            'obspy',
            'numpy',
            'tqdm',
            'Pwm',
        ],
    )
