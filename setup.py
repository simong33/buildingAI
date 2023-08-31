from setuptools import find_packages
from setuptools import setup

with open("requirements_prod.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(
    name="buildingAI",
    version="0.0.1",
    description="BuildingAI Model (api_pred)",
    license="MIT",
    author="FAST - Le Wagon Batch 1310",
    author_email="simon.guillorit@gmail.com",
    url="https://github.com/simong33/buildingAI/",
    install_requires=requirements,
    packages=find_packages(),
    # test_suite="tests",
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    zip_safe=False,
)
