# from plone.app.widgets.dx import DatetimeWidgetConverter as BaseDatetimeWidgetConvertor
# from plone.app.widgets.dx import DatetimeWidget
# from plone.app.widgets.dx import IDatetimeWidget
# from zope.component import adapts
# from zope.schema.interfaces import IDatetime
# import types


# class DatetimeWidgetConverter(BaseDatetimeWidgetConvertor):
#     adapts(IDatetime, IDatetimeWidget)

#     def toWidgetValue(self, value):
#         if isinstance(value, types.MethodType):
#             value = value().asdatetime()
#         res = super(DatetimeWidgetConverter, self).toWidgetValue(value)
#         return res


# DatetimeWidget._convertor = DatetimeWidgetConverter
