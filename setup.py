import shlex
from subprocess import check_output, CalledProcessError
from setuptools import setup, find_packages
import datetime


DEFAULT_VERSION=f"99.99.99+devdirty"

LONG_DESCRIPTION="""
This package contains a CLI to build up some Linux images using yocto.
"""

def git_to_pep440(git_version):
    """ Transforms the git version to an allowed pep404 version = vx.y.z.dev<SHORT_SHA_NUM>. """
    if '-' not in git_version:
        return git_version

    cmd = 'git rev-parse --short HEAD'
    sha = check_output(shlex.split(cmd)).decode('utf-8')
    sep = git_version.index('-')
    version = git_version[:sep] + '.dev' + str(int(sha, 16))
    return version


def git_version() -> str:
    """ Use git latest tag to determine the version of the package.

    :return: the short SHA of the git repository.
    """
    cmd = 'git describe --tags --always --dirty --match v[0-9]*'
    try:
        git_version = check_output(shlex.split(cmd)).decode('utf-8').strip()[1:]
        version = git_to_pep440(git_version)
    except CalledProcessError as e:
        print(f'Could not get git version, using a default version ({e})')
        version = DEFAULT_VERSION + "." + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return version


def read_requirements(requirements_file: str) -> list:
    """ Read a requirements file and return its content.

    :param requirements_file: the file that holds the requirements.
    :returns: a list with all the requirements stored in the file
    """
    with open(requirements_file) as f:
        install_requires = f.read().splitlines()

    return install_requires


setup(
    name="yoctales",
    version=git_version(),
    description="Tool used to build linux images using yocto.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/marifante/yocto_tales",
    author="Julian Rodriguez",
    author_email="junirodriguezz1@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "yoctales=yoctales.cli:main",
        ],
    },
    python_requires=">=3.7, <4",
    install_requires=read_requirements("requirements.txt")
)
