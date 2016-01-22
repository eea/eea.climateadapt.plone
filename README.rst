======================
EEA Climate Adapt
======================
.. image:: http://ci.eionet.europa.eu/job/eea.climateadapt-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.climateadapt-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.climateadapt-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.climateadapt-plone4/lastBuild

EEA Package

Contents
========

.. contents::

Main features
=============

1.
2.
3.

Install
=======

- Add eea.climateadapt to your eggs section in your buildout and re-run buildout.
  You can download a sample buildout from
  https://github.com/eea/eea.climateadapt/tree/master/buildouts/plone4
- Install eea.climateadapt within Site Setup > Add-ons

Getting started
===============

1.
2.
3.

Dependencies
============

1.
2.
3.

Test locally
============

To test the view,
create a folder and navigate to http://localhost:8080/Plone/folder/@@sat_view,
or go into the ZMI
and set the property ``layout`` of the folder to ``@@sat_view``.

Since the SAT view contacts a Geoserver instance via Javascript,
and we don't set up a geoserver locally,
but instead connect directly to the production one, there is an issues with CORS.

In order to mitigate that,
download and install CORSProxy (https://github.com/gr2m/CORS-Proxy)
and then launch it in a shell.

Then relaunch the instance like this::

  $ CORS_PROXY_DEVEL=http://localhost:1337 bin/instance fg

Plone will rewrite the base URL to pass through the proxy
and not have preflight requests fail.

Source code
===========

- Latest source code (Plone 4 compatible):
  https://github.com/eea/eea.climateadapt


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Progress Bar (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
