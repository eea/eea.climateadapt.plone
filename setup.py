import os

from setuptools import find_packages, setup

NAME = "eea.climateadapt"
PATH = NAME.split(".") + ["version.txt"]
VERSION = open(os.path.join(*PATH)).read().strip()


long_description = '\n\n'.join(
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
        # laszlo remove "setuptools",
        # laszlo remove "plone.app.dexterity",
        # laszlo remove "plone.namedfile [blobs]",
        # -*- Extra requirements: -*-
        # laszlo remove "z3c.jbot",
        # laszlo remove "pycountry",
        # laszlo remove "collective.dexteritytextindexer",
        # laszlo remove "collective.easyform",
        # laszlo remove "tokenlib",
        # laszlo remove "eea.rabbitmq.client",  # schedule jobs
        # laszlo remove "eea.rabbitmq.plone",
        # laszlo remove "langdetect",
        # laszlo remove "chardet",
        # laszlo remove "zeep==3.4.0", 
        # "google-api-python-client",  # google analytics API integration
        # "collective.relationhelpers",
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
      climateadapt_importer = eea.climateadapt._importer:main
      sync_to_arcgis = eea.climateadapt.scripts.sync_to_arcgis:main
      arcgis_cli = eea.climateadapt.scripts.cli_arcgis_client:main
      c3s = eea.climateadapt.scripts.c3s:main
      get_broken_links = eea.climateadapt.browser.scripts:get_broken_links
      sync_adaptecca_casestudies = eea.climateadapt.browser.scripts:sync_adaptecca_casestudies
      import_drmkc = eea.climateadapt.browser.scripts:import_drmkc
      archive_news = eea.climateadapt.browser.scripts:archive_news
      harvest_eea_indicators = eea.climateadapt.scripts.harvest_eea_indicators:main
      refresh_analytics_data = eea.climateadapt.browser.admin:refresh_analytics_data
      run_translation_step_2 = eea.climateadapt.translation.scripts.translation:translation_step_2
      migrate_to_volto = eea.climateadapt.migration.scripts:migrate_to_volto
      """,
    # The next two lines may be deleted after you no longer need
    # addcontent support from paster and before you distribute
    # your package.
    # setup_requires=["PasteScript"],
    # paster_plugins=["templer.localcommands"],
    # refresh_analytics_data = eea.climateadapt.browser.admin:refresh_analytics_data
)
