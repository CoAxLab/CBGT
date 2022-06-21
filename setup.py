from setuptools import setup, find_packages
from setuptools import Extension
import numpy as np

# UPDATE PYPI RELEASE (Version Update)
# pip install --upgrade setuptools wheel twine

# git commit -am "update demo, bump version patch"; git push origin master; python setup.py sdist bdist_wheel; twine upload dist/CBGT-0.0.6*

ext_modules = [Extension('cbgt', ['src/cbgt.c'])]
package_data = {'cbgt': ['src/*.c', 'src/*.h', 'docs/*.md',
                'docs/*.txt', 'params/*.py', 'params/*.tex']}
cbgt_packages = ['cbgt', 'cbgt.src']

setup(
    name='CBGT',
    version='0.0.6',
    author='Kyle Dunovan, Catalina Vich, Matthew Clapp, Timothy Verstynen, Jonathan Rubin, Wei Wei, and Xiao Jing Wang',
    author_email='dunovank@gmail.com',
    url='http://github.com/CoAxLab/CBGT',
    packages=cbgt_packages,
    package_data=package_data,
    description='CBGT contains code for implementing the CBGT network and drift-diffusion model (DDM) fits described in the manuscript Reward-driven changes in striatal pathway competition shape evidence evaluation in decision-making.',
    install_requires=['numpy==1.22.0', 'pandas>=0.15.1', 'matplotlib>=1.4.3', 'seaborn>=0.5.1', 'future'],
    setup_requires=['numpy==1.22.0', 'pandas>=0.15.1', 'matplotlib>=1.4.3', 'seaborn>=0.5.1', 'future'],
    include_dirs = [np.get_include()],
    classifiers=['Environment :: Console',
                'Operating System :: OS Independent',
                'License :: OSI Approved :: BSD License',
                'Intended Audience :: Science/Research',
                'Development Status :: 3 - Alpha',
                'Programming Language :: Python',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.6',
                'Topic :: Scientific/Engineering',
                 ],
    ext_modules = ext_modules
)
