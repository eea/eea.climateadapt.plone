import datetime

from DateTime import DateTime
from z3c.form.datamanager import AttributeField

# [{'error': WrongType(DateTime('2023/09/19 11:42:44.509733 GMT+2'), <type 'datetime.datetime'>, 'modification_date'),
#   'field': 'modification_date',
#   'message': u'Object is of wrong type.'},

#  {'error': WrongType('eea.climateadapt.indicator.2023-09-19.5645058654', <type 'unicode'>, 'id'),
#   'field': 'id',
#   'message': u'Object is of wrong type.'},

#  {'error': WrongType('', <type 'unicode'>, 'description'),
#   'field': 'description',
#   'message': u'Object is of wrong type.'},

#  {'error': WrongType('eea.climateadapt.indicator', <type 'unicode'>, 'portal_type'),
#   'field': 'portal_type',
#   'message': u'Object is of wrong type.'},
#  {'error': WrongType(DateTime('2023/09/19 11:42:44.509733 GMT+2'), <type 'datetime.datetime'>, 'creation_date'),
#   'field': 'creation_date',
#   'message': u'Object is of wrong type.'}]

# data managers that fix the fields for restapi

# ('contributor_list', <plone.app.relationfield.widget.RelationListDataManager object at 0x7fc655d5b110>)
# ('long_description', <z3c.form.datamanager.AttributeField object at 0x7fc656681350>)
# ('include_in_observatory', <z3c.form.datamanager.AttributeField object at 0x7fc655b37cd0>)
# ('title', <z3c.form.datamanager.AttributeField object at 0x7fc656996f50>)
# ('comments', <z3c.form.datamanager.AttributeField object at 0x7fc6a0d19690>)
# ('include_in_mission', <z3c.form.datamanager.AttributeField object at 0x7fc656797690>)
# ('publication_date', <z3c.form.datamanager.AttributeField object at 0x7fc656996f50>)
# ('geochars', <z3c.form.datamanager.AttributeField object at 0x7fc6a0d19690>)
# ('sectors', <z3c.form.datamanager.AttributeField object at 0x7fc656797690>)
# ('other_contributor', <z3c.form.datamanager.AttributeField object at 0x7fc655dc4d50>)
# ('climate_impacts', <z3c.form.datamanager.AttributeField object at 0x7fc6a0d19690>)
# ('relatedItems', <plone.app.relationfield.widget.RelationListDataManager object at 0x7fc655ceb3d0>)

# 'modification_date', 'id', 'description', 'portal_type', 'creation_date']


class CustomAttributeFieldDataManager(AttributeField):

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        value = super(CustomAttributeFieldDataManager, self).get()

        if self.field.__name__ in ['id', 'description', 'portal_type']:
            if isinstance(value, unicode):
                value = str(value)
                print(self.field.__name__, value)

        elif self.field.__name__ in ['modification_date', 'creation_date']:
            if isinstance(value, DateTime):
                value = value.asdatetime()
                print(self.field.__name__, value)

        return value
