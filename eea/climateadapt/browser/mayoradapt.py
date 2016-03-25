# coding=utf-8
import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class IMAdaptView (Interface):
    """ Countries Interface """


class MAdaptView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/mayors-adapt """

    implements(IMAdaptView)


class b_m_climate_impacts (BrowserView):
    def __call__(self):
        return """["Droughts","Extreme Temperatures","Flooding","Forest Fires","Ice and Snow","Sea Level Rise","Storms","Water Scarcity"]"""


class a_m_country (BrowserView):
    def __call__(self):
        return """["Albania","Austria","Belgium","Bulgaria","Bosnia and Herzegovina","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","Former Yugoslav Republic of Macedonia","France","Germany","Greece","Hungary","Iceland","Ireland","Italy","Kosovo under UN Security Council Resolution 124","Latvia","Liechtenstein","Lithuania","Luxembourg","Malta","Montenegro","Netherlands","Norway","Poland","Portugal","Romania","Serbia","Slovakia","Slovenia","Spain","Sweden","Switzerland","Turkey","United Kingdom"]"""


class b_m_sector (BrowserView):
    def __call__(self):
        return """["Agriculture and Forest","Biodiversity","Coastal areas","Disaster Risk Reduction","Energy","Financial","Health","Infrastructure","Marine and Fisheries","Tourism","Urban","Water Management","Other"]"""


class c_m_stage_of_the_implementation_cycle (BrowserView):
    def __call__(self):
        return """["Preparing the ground","Assessing risks and vulnerabilities","Identifying adaptation options","Assessing adaptation options","Implementation","Monitoring and evaluation"]"""


class citiesxyz (BrowserView):
    def __call__(self):
        return """{"Aachen":"/-/aachen","Agioi Anargyroi-Kamatero":"/-/agioi-anargyroi-kamatero","Agueda":"/-/agueda","Alimos":"/-/alimos","Anadia":"/-/anadia","Andrano":"/-/andrano","Antwerp":"/-/antwe-1","Antwerp Province":"/-/antwerp-province","Arnhem":"/-/arnhem","Arnsberg":"/-/arnsbe-1","Barcelona":"/-/barcelona","Bologna":"/-/bologna","Bullas":"/-/bullas","Burgas":"/-/burgas","Carmignano di Brenta":"/-/carmignano-di-brenta","Cascais":"/-/cascais","Copenhagen":"/-/copenhagen","Craco":"/-/comune-di-craco","Daruvar":"/-/daruvar","Edinburgh":"/-/edinburgh","Elmshorn":"/-/elmshorn","Farsala":"/-/farsala","Frankfurt am Main":"/-/frankfurt-am-main","Ghent":"/-/ghent","Glasgow":"/-/glasgow","Granollers":"/-/granollers","Greater Manchester":"/-/greater-manchester","Hannover":"/-/hannover","Hasselt":"/-/hasselt","Kochani":"/-/kochani","Leicester":"/-/leicester","Madrid":"/-/madrid","Molina de Segura":"/-/molina-de-segura","Munich":"/-/munich","Murcia":"/-/murcia","Münster":"/-/munster","Newcastle upon Tyne":"/-/newcastle-upon-tyne","Nijmegen":"/-/nijmegen","Pontevico":"/-/pontevico","Puerto Lumbreras":"/-/puerto-lumbreras","Reggio Emilia":"/-/reggio-emilia","Rende":"/-/rende","Reykjavik":"/-/reykjavik","San Benedetto del Tronto":"/-/san-benedetto-del-tronto","Sant Cugat del Valles":"/-/sant-cugat-del-valles","Silvi":"/-/silvi","Smolyan":"/-/smolyan","Sorradile":"/-/sorradile","Stirling":"/-/stirling-council","Stockholm":"/-/stockholm","Stuttgart":"/-/stuttgart","Torres Vedras":"/-/torres-vedras","Toulouse Métropole":"/-/toulouse-metropole","Treviso":"/-/treviso","Vagos":"/-/vagos","Valka":"/-/valka","Vicenza":"/-/vicenza","Vila do Conde":"/-/vila-do-conde","Växjö":"/-/vaxjo","Worms":"/-/worms","Wuppertal":"/-/wuppertal","Zwijndrecht":"/-/zwijndrecht","Ílhavo":"/-/ilhavo"}"""
