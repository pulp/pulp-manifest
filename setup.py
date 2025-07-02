from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="pulp_manifest",
    version="3.1.0",
    license="GPLv2+",
    packages=find_packages(),
    author="Pulp Team",
    author_email="pulp-list@redhat.com",
    description="Tool to generate a PULP_MANIFEST file for a given directory,"
    " so the directory can be recognized by Pulp.",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pulp-manifest = pulp_manifest.build_manifest:main",
        ]
    },
)
