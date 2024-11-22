from zope.interface import alsoProvides
from eea.climateadapt import CcaAdminMessageFactory as _
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider
from zope.schema import (Bool, Choice, List)


@provider(IFormFieldProvider)
class IHealthObservatoryMetadata(model.Schema):
    model.fieldset(
        "health_inclusion",
        label="Inclusion in the subsites",
        fields=["include_in_observatory",
                "include_in_mission", "health_impacts"],
    )

    include_in_observatory = Bool(
        title=_("Include in observatory"), required=False, default=False
    )

    include_in_mission = Bool(
        title=_("Include in the Mission Portal"), required=False, default=False
    )

    health_impacts = List(
        title=_("Health impacts"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.health_impacts"),
    )


alsoProvides(IHealthObservatoryMetadata["include_in_observatory"], ILanguageIndependentField)
alsoProvides(IHealthObservatoryMetadata["include_in_mission"], ILanguageIndependentField)
alsoProvides(IHealthObservatoryMetadata["health_impacts"], ILanguageIndependentField)
