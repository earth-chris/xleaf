import os.path as osp

from numpy.distutils.core import Extension, setup

this_dir, this_path = osp.split(osp.abspath(__file__))
version = open(osp.join(this_dir, "xleaf", "__version__.py")).read().strip('"\n')
long_description = open(osp.join(this_dir, "README.md"), "r", encoding="utf-8").read()
requirements = open(osp.join(this_dir, "requirements.txt"), "r", encoding="utf-8").read().strip().split()

fortran_files = [
    "MODULE_PRO4SAIL.f90",
    "dataSpec_PDB.f90",
    "main_PROSAIL.f90",
    "LIDF.f90",
    "dladgen.f",
    "PRO4SAIL.f90",
    "prospect_DB.f90",
    "tav_abs.f90",
    "volscatt.f90",
]

setup_args = {
    "name": "xleaf",
    "version": version,
    "url": "https://github.com/earth-chris/xleaf",
    "license": "MIT",
    "author": "Christopher Anderson",
    "author_email": "cbanders@stanford.edu",
    "description": "Leaf and canopy radiative transfer modeling tools built on PROSPECT-D and SAIL",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "keywords": [
        "prospect",
        "sail",
        "prosail",
        "radiative transfer modeling",
        "simulation modeling",
        "remote sensing",
        "python",
    ],
    "packages": ["xleaf"],
    "install_requires": requirements,
    "python_requires": ">=3.7.0",
    "platforms": "any",
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    "ext_modules": [Extension(name="xleaf.prosail", sources=[osp.join("prosail", file) for file in fortran_files])],
}

setup(**setup_args)
