import os

from setuptools import find_packages, setup

NAME = "eea.climateadapt"
PATH = NAME.split(".") + ["version.txt"]
VERSION = open(os.path.join(*PATH)).read().strip()


long_description = "\n\n".join(
    (
        open("README.rst").read()
        + "\n"
        + open(os.path.join("docs", "HISTORY.txt")).read()
    ),
)

setup(
    name="eea.climateadapt",
    version=VERSION,
    description="EEA ClimateAdapt for Plone",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="eea zope plone python",
    author="European Environment Agency",
    author_email="webadmin@eea.europa.eu",
    url="http://eea.github.io",
    license="gpl",
    packages=find_packages(),
    # package_dir = {'': 'eea'},
    namespace_packages=["eea"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        "z3c.jbot",
        "pycountry",
        "tokenlib",
        "langdetect",
        "chardet",
        "zeep==3.4.0",
        "XlsxWriter==1.2.7",
        "collective.geolocationbehavior",
        "redis",  # do we need it?
        "bullmq",
        # "google-api-python-client",  # google analytics API integration
    ],
    extras_require={
        "test": [
            "plone.app.testing",
        ],
        "importer": [
            "zope.sqlalchemy",
            "psycopg2",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      [console_scripts]
      report_roles = eea.climateadapt.scripts.report_roles:main
      migrate_eionet_groups = eea.climateadapt.scripts.migrate_eionet_groups:main
      document_workflows = eea.climateadapt.scripts.document_workflows:main
      analyze_relstorage = eea.climateadapt.scripts.analyze_relstorage:main
      """,
)
