""" Importing utils
"""

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import SnapshotImportContext
from Products.GenericSetup.interfaces import IBody
from bs4 import BeautifulSoup
from collections import defaultdict
from collective.cover.tiles.configuration import TilesConfigurationScreen
from collective.easyform.api import CONTEXT_KEY
from collective.easyform.api import set_actions, set_fields
from decimal import Decimal
from eea.climateadapt._importer import sqlschema as sql
from eea.facetednavigation.events import FacetedEnabledEvent
from eea.facetednavigation.events import FacetedWillBeEnabledEvent
from eea.facetednavigation.interfaces import IDisableSmartFacets
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.interfaces import IHidePloneLeftColumn
from eea.facetednavigation.interfaces import IHidePloneRightColumn
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.supermodel import loadString
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.site.hooks import getSite
import logging
import lxml.etree
import lxml.html
import random
import re
import urllib.parse


logger = logging.getLogger('eea.climateadapt.importer')
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler())
# f.open('errorslog.txt', 'w+')

ACE_ITEM_TYPES = {
    'DOCUMENT': 'eea.climateadapt.publicationreport',
    'INFORMATIONSOURCE': 'eea.climateadapt.informationportal',
    'GUIDANCE': 'eea.climateadapt.guidancedocument',
    'TOOL': 'eea.climateadapt.tool',
    'ORGANISATION': 'eea.climateadapt.organisation',
    'INDICATOR': 'eea.climateadapt.indicator',
    'MAPGRAPHDATASET': 'eea.climateadapt.mapgraphdataset',
    'RESEARCHPROJECT': 'eea.climateadapt.researchproject',
    'ACTION': 'eea.climateadapt.action',
}


def createAndPublishContentInContainer(*args, **kwargs):
    """ Wrap createContentInContainer and publish it """

    content = createContentInContainer(*args, **kwargs)
    wftool = getToolByName(content, "portal_workflow")

    _publish = kwargs.get('_publish', True)
    if (args[1] not in ('File', 'Image',)) and _publish:
        try:
            wftool.doActionFor(content, 'immediately_publish')
        except WorkflowException:
            # a workflow exception is risen if the state transition is not available
            # (the sampleProperty content is in a workflow state which
            # does not have a "submit" transition)
            logger.error("Could not publish:" + content)
            raise

    return content


def printe(e):
    """ debug function to easily see an etree as pretty printed xml"""
    print(lxml.etree.tostring(e, pretty_print=True))


def s2l(text, separator=';', separators=None, relaxed=False):
    """Converts a string in form: u'EXTREMETEMP;FLOODING;' to a list"""

    if separators is None:
        if relaxed:
            separators = [';', ',', ' ']
        else:
            separators = [separator]

    if not text:
        return None

    # for specialtagging, the separator can be anything from
    # ' ' or ',' or ';'
    tags = [text]
    for sep in separators:
        z = [t.split(sep) for t in tags]
        tags = []
        for t in z:
            tags.extend(t)
        tags = [_f for _f in [x.strip() for x in tags] if _f]
        # TODO: lower() used to be called on some of this relaxed tags

    tags = [c.strip() for c in tags]
    return tags


def s2li(text, separator=';', relaxed=False):
    """Converts a string in form: u'123;456;' to a list of int"""
    if text:
        return list(map(int, s2l(text, separator=separator, relaxed=relaxed)))
    return None


def t2r(text):
    if text:
        if not text.startswith('<'):
            text = "<div>{0}</div>".format(text)
    return RichTextValue(text or '', 'text/html', 'text/html')


def r2t(text):
    # convert html strings to plain text
    nodes = lxml.html.fragments_fromstring(text)
    if nodes and isinstance(nodes[0], str):
        # a plain text is not converted to etree by lxml
        try:
            return '\r'.join(nodes).strip()
        except:
            return nodes[0] # junk in the rest of the file
    return '\r'.join([t.text_content() for t in nodes]).strip()


def to_decimal(val):
    if not isinstance(val, float):
        raise ValueError("Not a float: {0}".format(val))

    if val.hex() == 'nan':
        return None

    val = str(val)
    return Decimal(val)


def s2d(val):
    try:
        val = Decimal(val)
        return val
    except Exception:
        return None


def parse_settings(text):
    """Changes a string in form:
    # u'sitemap-changefreq=daily\nlayout-template-id=2_columns_iii\nsitemap-include=1\ncolumn-2=56_INSTANCE_9tMz,\ncolumn-1=56_INSTANCE_2cAx,56_INSTANCE_TN6e,\n'
    to a dictionary of settings
    """
    out = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        k, v = line.split('=', 1)
        v = [_f for _f in v.split(',') if _f]
        # if len(v) == 1:
        #     v = v[0]
        out[k] = v
    return out


def is_html(text):
    """ Returns true if the given text contains HTML"""
    return bool(BeautifulSoup(text or '', "html.parser").find())


def detect_richtext_fields(session):
    """ Detect all the fields that contain richtext.
    """
    result = {}
    for klass in [sql.AceAceitem, sql.AceProject, sql.AceMeasure]:
        print("Looking up", klass)
        richtext = set()
        for obj in session.query(klass):
            for name in list(obj.__dict__.keys()):
                if name in richtext:
                    continue
                value = getattr(obj, name)
                if isinstance(value, str):
                    if is_html(value):
                        richtext.add(name)
        result[klass] = richtext
    for k, v in list(result.items()):
        print("=" * 20)
        print("Richtext fields for ", k, ": ", v)


def solve_dynamic_element(node):
    """ Used to extract content from xml etree. This is content stored by journal article
    """

    type_ = node.get('type')

    if type_ == 'image':
        imageid = [str(x) for x in node.xpath("dynamic-content/@id")]
        if not imageid:
            imageid = node.xpath('dynamic-content/text()')
            if imageid:
                imageid = get_param_from_link(imageid[0], 'img_id')
            else:
                return ('image', node.get('name'), None)
        return ('image', node.get('name'), imageid)

    if type_ == 'text_area':
        return ('text',
                node.get('name'),
                [str(x) for x in node.xpath("dynamic-content/text()")]
                )

    if type_ == 'text_box':
        return (
            'dynamic',
            node.get('name'),
            [SOLVERS[child.tag](child) for child in node]
        )

    if type_ == 'text':
        return (
            'dynamic',
            node.get('name'),
            [SOLVERS[child.tag](child) for child in node]
        )

    if type_ in (None, 'list', 'boolean'):
        return (
            type_,
            node.get('name'),
            [SOLVERS[child.tag](child) for child in node]
        )

    raise ValueError("Dynamic element not handled, please write more code")


def solve_dynamic_content(node):
    # one of:
    #
    # <dynamic-content language-id="en_GB">1435190400000</dynamic-content>
    #
    # or:
    #
    # <dynamic-content language-id="en_GB">
    #         <option>Extreme Temperatures</option>
    #         <option>Flooding</option>
    #         <option>Sea Level Rise</option>
    # </dynamic-content>

    if not node.xpath('*'):
        return node.text
    return [x.text for x in node.iterchildren()]

    # return ('text', None, node.text)


def solve_static_content(node):
    return node.text
    # return ('text', None, node.text)


SOLVERS = {
    'dynamic-element': solve_dynamic_element,
    'static-content': solve_static_content,
    'dynamic-content': solve_dynamic_content,
    # 'static-element': solve_static_element,
}


def strip_xml(xmlstr):
    if ("<xml" in xmlstr) or ("<?xml" in xmlstr):
        res = str(lxml.etree.fromstring(xmlstr.encode('utf-8')).xpath(
            "*/text()")[0])
    else:
        res = str(xmlstr)
    return res


def _clean(s):
    if s in ["NULL_VALUE", 'all']:
        return None

    if isinstance(s, (list, tuple)):
        s = [_clean(x) for x in s]

    return s


def _clean_portlet_settings(d):

    _conv = {
        'aceitemtype': 'search_type',
        'anyOfThese': 'special_tags',
        #'anyOfThese': 'search_text',
        'countries': 'countries',
        # 'element': 'elements',
        'element': 'element_type',
        'nrItemsPage': 'count',
        'portletSetupTitle_en_GB': 'title',
        'sector': 'sector',
        'sortBy': 'sortBy',
        'css_class': 'css_class',
    }

    res = {}
    for k, v in list(d.items()):
        if k not in _conv:
            continue
        res[_conv[k]] = _clean(v)

    if d.get('anyOfThese'):
        text = res.get('search_text', ' ')
        text += d['anyOfThese']
        res['search_text'] = text.strip()

    if res.get('count'):
        res['nr_items'] = int(res['count'])

    # change back search_type to be a list
    if 'search_type' in res:
        search_type = res['search_type']
        if isinstance(search_type, str):
            res['search_type'] = [search_type]

    if 'userdefaultsector' in d:
        v = _clean(d['userdefaultsector'])
        if v:
            l = res.get('sector') or []
            l.append(v)
            res['sector'] = list(set(l))

    # change back sector to be a list
    if 'sector' in res:
        sector = res['sector']
        if isinstance(sector, str):
            res['sector'] = [sector]

    # change back element to be a list
    if 'element_type' in res:
        element_type = res['element_type']
        if isinstance(element_type, str):
            res['element_type'] = [element_type]

    return res


def _get_portlet(session, portletid, layout):
    """ Get the portlet based on portletid and layout.plid

    layout.plid is the "portlet instance id" """
    try:
        portlet = session.query(sql.Portletpreference).filter_by(
            portletid=portletid, plid=layout.plid,
        ).one()
        return portlet
    except:
        return None


def _get_article_for_portlet(session, portlet):
    """ Parse portlet preferences to get the Journalarticle for the portlet """

    e = lxml.etree.fromstring(portlet.preferences)

    try:
        articleid = e.xpath(
            '//name[contains(text(), "articleId")]'
            '/following-sibling::value'
        )[0].text
    except IndexError:
        logger.debug("Couldn't find an article for portlet %s",
                        portlet.portletid)
        return

    article = session.query(sql.Journalarticle).filter_by(
        articleid=articleid, status=0).order_by(
            sql.Journalarticle.version.desc()
        ).first()

    return article


def extract_portlet_info(session, portletid, layout):
    """ Extract portlet information from the portlet with portletid

    The result can vary, based on what we find in a portlet.

    It can be:
        * a simple string with text
        * a list of ('type_of_info', info)
    """
    portlet = _get_portlet(session, portletid, layout)
    if portlet is None:
        logger.debug("Portlet id: %s could not be found for %s",
                       portletid, layout.friendlyurl)
        return

    if not portlet.preferences:
        logger.warning("Couldn't get preferences for portlet %s with plid %s",
                       portlet.portletid, portlet.plid)
        return

    # extract portlet settings, must be an application's settings
    e = lxml.etree.fromstring(portlet.preferences)
    prefs = {}
    for pref in e.xpath('//preference'):
        name = str(pref.find('name').text)
        values = pref.findall('value')
        res = []
        for node in values:
            try:
                value = node.text
            except Exception:
                continue
            if value is not None:
                res.append(str(value))
        if len(res) == 0:
            prefs[name] = None
        elif len(res) == 1:
            prefs[name] = res[0]
        else:
            prefs[name] = res

    portlet_title = None
    if prefs.get('portletSetupUseCustomTitle') == "true":
        for k, v in list(prefs.items()):
            if k.startswith('portletSetupTitle'):
                portlet_title = str(v)

    article = _get_article_for_portlet(session, portlet)
    if article is not None:
        e = lxml.etree.fromstring(article.content.encode('utf-8'))

        # TODO: attach other needed metadata
        return {'title': article.title,
                'description': article.description,
                'content': [SOLVERS[child.tag](child) for child in e],
                'portlet_title': portlet_title,
                'portlet_type': 'journal_article_content'
                }

    logger.debug("Could not get an article from portlet %s for %s",
                    portletid, layout.friendlyurl)

    return prefs


def extract_simplified_info_from_article_content(content):
    e = lxml.etree.fromstring(content.encode('utf-8'))
    content = [SOLVERS[child.tag](child) for child in e]
    return content


def get_template_for_layout(layout):
    settings = parse_settings(layout.typesettings)

    if layout.type_ == 'link_to_layout':
        return "link to layout"

    template = settings['layout-template-id'][0]
    return template


def make_tile(cover, col, css_class=None, no_titles=False):
    # TODO: this should be able to return a list of tiles from the column
    # not just a single tile

    tile_name = col[0][0]
    payload = col[0][1]

    if css_class:
        payload['css_class'] = css_class

    if tile_name.startswith('iframe'):
        return make_iframe_embed_tile(cover, payload['url'])
    elif 'webformportlet' in tile_name:
        return make_form_tile(cover, payload)
    elif 'ASTHeaderportlet' in tile_name:
        return make_ast_header_tile(cover, payload)

    if payload.get('portlet_type') == 'journal_article_content':
        main_text = make_text_from_articlejournal(payload['content'])
        _content = {
            'title': payload['portlet_title'] or "",
            'text': main_text,
            'css_class': css_class
        }
        if no_titles:
            return make_richtext_tile(cover, _content)
        else:
            return make_richtext_with_title_tile(cover, _content)

    if payload.get('freeparameter') == '1':
        return make_aceitem_filter_tile(cover, payload)

    if tile_name and 'SimpleFilterportlet' in tile_name:
        return make_aceitem_relevant_content_tile(cover, payload)

    if payload.get('paging') == '1':
        # this is the search portlet on the right
        return make_aceitem_search_tile(cover, payload)
    else:
        print("Fallback tile")
        return make_aceitem_relevant_content_tile(cover, payload)


def make_tiles(cover, column, css_class=None):
    return [make_tile(cover, [portlet], css_class) for portlet in column]


def make_ast_header_tile(cover, payload):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.ast_header'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    info = {'title': payload['headertext'], 'step': int(payload['step'])}
    ITileDataManager(tile).set(info)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def get_form_fields(content):
    fields_types = [k for k in list(content.keys()) if k.startswith('fieldType')]
    fields = []
    for f in sorted(fields_types):
        if not content.get(f):
            continue
        field = {}
        fname = f.replace('fieldType','')
        foptional = content.get('fieldOptional{fname}'.format(fname=fname))
        frequired = foptional == 'false' and True or False
        field['name'] = fname
        field['required'] = frequired
        field['options'] = content.get(
            'fieldOptions{fname}'.format(fname=fname))
        field['label'] = content.get(
            'fieldLabel{fname}'.format(fname=fname))
        field['type'] = content.get(
            'fieldType{fname}'.format(fname=fname))
        field['validation_error'] = content.get(
            'fieldValidationErrorMessage{fname}'.format(fname=fname))
        field['validation_script'] = content.get(
            'fieldValidationScript{fname}'.format(fname=fname))
        fields.append(field)
    return fields


def make_form_fields_model(form_obj, content):
    form_fields = get_form_fields(content)
    nsmap = {}
    easyformns = "http://namespaces.plone.org/supermodel/easyform"
    efns = "{ns}".format(ns=easyformns)
    nsmap[None] = "http://namespaces.plone.org/supermodel/schema"
    nsmap['security'] = "http://namespaces.plone.org/supermodel/security"
    nsmap['marshal'] = "http://namespaces.plone.org/supermodel/marshal"
    nsmap['form'] = "http://namespaces.plone.org/supermodel/form"
    nsmap['easyform'] = easyformns
    model = lxml.etree.Element('model', nsmap=nsmap)
    schema = lxml.etree.SubElement(model, 'schema')

    # <field
    #         name="replyto"
    #         type="zope.schema.TextLine"
    #         easyform:TDefault="python:member and member.getProperty(\'email\', \'\') or \'\'"
    #         easyform:serverSide="False"
    #         easyform:validators="isValidEmail">
    #     <description/>
    #     <title>Your E-Mail Address</title>
    # </field>
    #

    for f in form_fields:
        validators = []
        field = lxml.etree.SubElement(schema, 'field')
        field.set('{{{ns}}}TDefault'.format(ns=efns), '')
        field.set('{{{ns}}}ServerSide'.format(ns=efns), 'False')
        field.set('name', 'field_{name}'.format(name=f['name']))
        title = lxml.etree.SubElement(field, 'title')
        title.text = f['label']
        lxml.etree.SubElement(field, 'description')
        req = lxml.etree.SubElement(field, 'required')
        req.text = str(f['required'])
        if f['type'] == 'text':
            field.set('type', 'zope.schema.TextLine')
            if f['label'].lower() == 'email':
                validators.append('isValidEmail')
        elif f['type'] == 'options':
            # https://github.com/plone/plone.supermodel/blob/master/plone/supermodel/fields.txt#L1237
            field.set('type', 'zope.schema.Choice')
            options = s2l(f['options'], separator=',')
            default_option = options[0]
            default = lxml.etree.SubElement(field, 'default')
            default.text = default_option
            lxml.etree.SubElement(field, 'missing_value')
            values = lxml.etree.SubElement(field, 'values')
            for o in options:
                opt = lxml.etree.SubElement(values, 'element')
                opt.text = o
        elif f['type'] == 'textarea':
            field.set('type', 'zope.schema.Text')
        validators_str = '|'.join(validators)
        field.set('{{{ns}}}validators'.format(ns=efns), validators_str)

    # captcha field don't work ok, disabling them temporarily
    # if content.get('requireCaptcha') == u'true':
    #     field = lxml.etree.SubElement(schema, 'field')
    #     field.set('{{{ns}}}TDefault'.format(ns=efns), '')
    #     field.set('{{{ns}}}ServerSide'.format(ns=efns), 'False')
    #     field.set('{{{ns}}}validators'.format(ns=efns), '')
    #     field.set('name', 'field_captcha')
    #     field.set('type', 'collective.easyform.fields.ReCaptcha')
    #     req = lxml.etree.SubElement(field, 'required')
    #     req.text = str(True)
    #     title = lxml.etree.SubElement(field, 'title')
    #     title.text = u'Text Verification'
    #     lxml.etree.SubElement(field, 'description')

    return lxml.etree.tostring(model)


def make_form_actions_model(form_obj, content):
    """
    The required action model should be like this:
    <model
      xmlns:form="http://namespaces.plone.org/supermodel/form"
      xmlns:easyform="http://namespaces.plone.org/supermodel/easyform"
      xmlns:indexer="http://namespaces.plone.org/supermodel/indexer"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      xmlns:security="http://namespaces.plone.org/supermodel/security"
      xmlns:marshal="http://namespaces.plone.org/supermodel/marshal"
      xmlns="http://namespaces.plone.org/supermodel/schema">
        <schema>
            <field name="mailer" type="collective.easyform.actions.Mailer">
            <body_pt>&lt;html xmlns="http://www.w3.org/1999/xhtml"&gt;&#13;
                &lt;head&gt;&lt;title&gt;&lt;/title&gt;&lt;/head&gt;&#13;
                &lt;body&gt;&#13;
                &lt;p tal:content="body_pre | nothing" /&gt;&#13;
                &lt;dl&gt;&#13;
                &lt;tal:block repeat="field data | nothing"&gt;&#13;
                &lt;dt tal:content="python:fields[field]" /&gt;&#13;
                &lt;dd tal:content="structure python:data[field]" /&gt;&#13;
                &lt;/tal:block&gt;&#13; &lt;/dl&gt;&#13;
                &lt;p tal:content="body_post | nothing" /&gt;&#13;
                &lt;pre tal:content="body_footer | nothing" /&gt;&#13;
                &lt;/body&gt;&#13;
                &lt;/html&gt;
            </body_pt>
            <description>E-Mails Form Input urban-climate-adaptation-contact-form-7</description>
            <msg_subject>New form submission for "Urban Climate Adaptation"</msg_subject>
            <recipientOverride>string: helpdesk@mayors-adapt.eu</recipientOverride>
            <replyto_field>replyto</replyto_field>
            <senderOverride>string: No reply1 &lt;no-reply@eea.europa.eu&gt;</senderOverride>
            <showFields/>
            <title>urban-climate-adaptation-contact-form-7</title>
            </field>
        </schema>
    </model>
    """
    nsmap = {}
    easyformns = "http://namespaces.plone.org/supermodel/easyform"
    # efns = "{ns}".format(ns=easyformns)
    nsmap[None] = "http://namespaces.plone.org/supermodel/schema"
    nsmap['security'] = "http://namespaces.plone.org/supermodel/security"
    nsmap['marshal'] = "http://namespaces.plone.org/supermodel/marshal"
    nsmap['form'] = "http://namespaces.plone.org/supermodel/form"
    nsmap['indexer'] = "http://namespaces.plone.org/supermodel/indexer"
    nsmap['i18n'] = "http://xml.zope.org/namespaces/i18n"
    nsmap['easyform'] = easyformns
    model = lxml.etree.Element('model', nsmap=nsmap)
    schema = lxml.etree.SubElement(model, 'schema')
    if content.get('sendAsEmail') == 'true':
        field = lxml.etree.SubElement(
            schema, 'field', name='mailer',
            type="collective.easyform.actions.Mailer")
        body_pt = lxml.etree.SubElement(field, 'body_pt')
        body_pt.text = """"<html xmlns="http://www.w3.org/1999/xhtml">
    <head><title></title></head>
        <body>
            <p tal:content="body_pre | nothing" />
            <dl>
                <tal:block repeat="field data | nothing">
                    <dt tal:content="python:fields[field]" />
                    <dd tal:content="structure python:data[field]" />
                </tal:block>
            </dl>
            <p tal:content="body_post | nothing" />
            <pre tal:content="body_footer | nothing" />
        </body>
    </html>"""
        description = lxml.etree.SubElement(field, 'description')
        description.text = 'E-Mails Form Input'
        msg_subject = lxml.etree.SubElement(field, 'msg_subject')
        msg_subject.text = content.get('subject')
        recipient_override = lxml.etree.SubElement(field, 'recipientOverride')
        recipient_override.text = 'string: {email}'.format(
            email=content.get('emailAddress'))
        replyto_field = lxml.etree.SubElement(field, 'replyto_field')
        replyto_field.text = 'replyto'
        sender_override = lxml.etree.SubElement(field, 'senderOverride')
        sender_override.text = 'string: {name} <{email}>'.format(
            name=content.get('emailFromName'),
            email=content.get('emailFromAddress'))
        lxml.etree.SubElement(field, 'showFields')
        title = lxml.etree.SubElement(field, 'title')
        title.text = 'Mailer'
    if content.get('saveToDatabase') == 'true':
        field = lxml.etree.SubElement(
            schema, 'field', name='store_submissions',
            type="collective.easyform.actions.SaveData")
        lxml.etree.SubElement(field, 'ExtraData')
        use_column_names = lxml.etree.SubElement(field, 'UseColumnNames')
        use_column_names.text = 'False'
        lxml.etree.SubElement(field, 'description')
        lxml.etree.SubElement(field, 'showFields')
        title = lxml.etree.SubElement(field, 'title')
        title.text = 'Stored form submissions'
    if content.get('saveToFile') == 'true':
        # TODO: this needs to be investigated
        pass
    return lxml.etree.tostring(model).decode()


def make_form_content(context, content):
    form_prologue = content.get('description').replace('[$NEW_LINE$]','<br />')
    form_obj = createAndPublishContentInContainer(
        context,
        'EasyForm',
        title=content.get('title'),
        submitLabel='Send'
    )
    form_prologue = '<p>{prologue}</p>'.format(prologue=form_prologue)
    form_obj.formPrologue = t2r(form_prologue)

    fields_model_str = make_form_fields_model(form_obj, content)
    fields_model = loadString(fields_model_str)
    fields_schema = fields_model.schema
    set_fields(form_obj, fields_schema)

    actions_model_str = make_form_actions_model(form_obj, content)
    actions_model = loadString(actions_model_str)
    actions_schema = actions_model.schema
    actions_schema.setTaggedValue(CONTEXT_KEY, form_obj)
    set_actions(form_obj, actions_schema)
    return form_obj


def make_form_tile(cover, content):
    # creates a new tile and saves it in the annotation
    # returns a python objects usable in the layout description
    # content needs to be a dict with keys 'title' and 'text'
    form_obj = make_form_content(cover.aq_parent, content)

    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.formtile'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    formtiledata = {}
    formtiledata['title'] = form_obj.get('title')
    formtiledata['form_uuid'] = form_obj.UID()

    ITileDataManager(tile).set(formtiledata)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_text_from_articlejournal(content):
    """ Converts an article journal to richtext.

    Uses the Readmore template if it detects the case
    """

    if not isinstance(content, list):
        raise ValueError

    if len(content) == 1:
        return content[0]

    if len(content) != 2:
        import pdb; pdb.set_trace()

    first_text = content[0][2][0]
    second_text = content[1][2][0]

    payload = {
        'first_text': first_text,
        'second_text': second_text
    }

    return render('templates/readmore_text.pt', payload)


def set_css_class(cover, tile, css_class):
    if css_class:
        tile_conf_adapter = TilesConfigurationScreen(cover, None, tile)

        conf = tile_conf_adapter.get_configuration()
        conf['css_class'] = css_class
        tile_conf_adapter.set_configuration(conf)


def make_aceitem_search_tile(cover, info):
    # Available options
    # title
    # search_text
    # element_type
    # sector
    # special_tags
    # countries

    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.search_acecontent'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    info = _clean_portlet_settings(info)

    css_class = info.pop('css_class', None)

    ITileDataManager(tile).set(info)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_transregion_dropdown_tile(cover, options=None):
    if options is None:
        options = {}
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.transregionselect'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    options.update({'title': "Trans regional select"})
    ITileDataManager(tile).set(options)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_ast_navigation_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.ast_navigation'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': "AST Navigation"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_urbanast_navigation_tile(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.urbanast_navigation'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': "UrbanAST Navigation"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_urbanmenu_title(cover):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.urbanmenu'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set({'title': "Urban Menu"})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_countries_dropdown_tile(cover, image=None):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.countryselect'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    uuid = None
    if image is not None:
        uuid = image.__dict__['_plone.uuid']

    ITileDataManager(tile).set({'title': "Country select", 'image_uuid': uuid})

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id,
    }


def make_aceitem_filter_tile(cover, payload):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.filter_acecontent'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    info = _clean_portlet_settings(payload)

    css_class = info.pop('css_class', None)
    ITileDataManager(tile).set(info)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_aceitem_relevant_content_tile(cover, payload):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.relevant_acecontent'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    info = _clean_portlet_settings(payload)

    css_class = info.pop('css_class', None)
    ITileDataManager(tile).set(info)

    # TODO: relevant stuff here
    # info = _clean_portlet_settings(payload)
    # if filter(lambda x: x.startswith('user'), payload.keys()):
    #     return make_aceitem_relevant_content_tile(cover, payload)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_richtext_tile(cover, content):
    # creates a new tile and saves it in the annotation
    # returns a python objects usable in the layout description
    # content needs to be a dict with keys 'title' and 'text'

    site = getSite()

    id = getUtility(IUUIDGenerator)()
    typeName = 'collective.cover.richtext'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    content['text'] = t2r(str(fix_links(site, str(content['text']))))
    content['title'] = str(content['title'])

    css_class = content.pop('css_class', None)

    ITileDataManager(tile).set(content)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_richtext_with_title_tile(cover, content):
    # creates a new tile and saves it in the annotation
    # returns a python objects usable in the layout description
    # content needs to be a dict with keys 'title' and 'text'

    site = getSite()

    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.richtext_with_title'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    content['text'] = t2r(fix_links(site, str(content['text'])))
    content['title'] = str(content['title'])
    content['dont_strip'] = True

    css_class = content.pop('css_class', None)

    ITileDataManager(tile).set(content)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_share_tile(cover, share_type):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.shareinfo'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))

    content = {}
    content['title'] = "Share your %s" % share_type
    content['shareinfo_type'] = share_type

    css_class = content.pop('css_class', None)

    ITileDataManager(tile).set(content)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


def make_iframe_embed_tile(cover, url):
    id = getUtility(IUUIDGenerator)()
    type_name = 'collective.cover.embed'
    tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))

    embed = """<iframe class='ace-iframe' frameborder='0'
        style='min-width:980px;min-height:700px' height='100%%'
        scrolling='no' src='%s'></iframe>""" % url

    titles = ['Exposure', 'Sensitivity', 'Response capacity']
    if cover.title in titles:
        embed = """<iframe class='ace-iframe' frameborder='0'
            style='min-width:780px;min-height:800px' height='100%%'
            scrolling='no' src='%s'></iframe>""" % url
    elif cover.title in ['My adaptation', 'Generic response']:
        embed = """<iframe class='ace-iframe' frameborder='0'
            style='min-width:940px;min-height:800px' height='100%%'
            scrolling='no' src='%s'></iframe>""" % url

    ITileDataManager(tile).set({'title': '', 'embed': embed})

    return {
        'tile-type': 'collective.cover.embed',
        'type': 'tile',
        'id': id
    }


def make_view_tile(cover, kw):
    id = getUtility(IUUIDGenerator)()
    typeName = 'eea.climateadapt.genericview'
    tile = cover.restrictedTraverse('@@%s/%s' % (typeName, id))
    ITileDataManager(tile).set(kw)

    return {
        'tile-type': typeName,
        'type': 'tile',
        'id': id
    }


# def make_ast_text_tile(cover, info):
#     id = getUtility(IUUIDGenerator)()
#     type_name = 'collective.cover.richtext'
#     tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))
#
#     payload = {
#         'title':None,
#         'subtitle': None,
#         'first_text': None,
#         'second_text': None,
#     }
#     country['Summary'] = render('templates/table.pt', table)
#
#     ITileDataManager(tile).set({'title': 'embeded iframe', 'embed': embed})
#
#     return {
#         'tile-type': 'collective.cover.embed',
#         'type': 'tile',
#         'id': id
#     }
#

def make_image_tile(site, cover, info):
    id = getUtility(IUUIDGenerator)()
    type_name = 'collective.cover.banner'
    tile = cover.restrictedTraverse('@@%s/%s' % (type_name, id))

    imageid = info['id']
    image = get_repofile_by_id(site, imageid)
    tile.populate_with_object(image)
    return {
        'tile-type': type_name,
        'type': 'tile',
        'id': id
    }


def make_layout(*rows):
    # creates a cover layout. Needs a list of rows

    # a layout contains rows
    # a row can contain columns (in its children).
    # a column will contain a group
    # a group will have the tile

    # sample cover layout. This is a JSON string!
    # cover_layout = [
    #     {"type": "row", "children":
    #      [{"type": "group",
    #        "children":
    #        [
    #            {"tile-type": "collective.cover.richtext", "type": "tile", "id": "be70f93bd1a4479f8a21ee595b001c06"}
    #         ],
    #        "roles": ["Manager"],
    #        "column-size": 8},
    #       {"type": "group",
    #        "children":
    #        [
    #            {"tile-type": "collective.cover.embed", "type": "tile", "id": "face16b81f2d46bc959df9da24407d94"}
    #        ],
    #        "roles": ["Manager"],
    #        "column-size": 8}]},
    #     {"type": "row",
    #      "children":
    #         [
    #             {"type": "group", "children":
    #              [
    #                  {"tile-type": "collective.cover.richtext", "type": "tile", "id": "a42d3c2a88c8430da52136e2a204cf25"}
    #               ],
    #              "roles": ["Manager"],
    #              "column-size": 16}]}
    # ]


    # [{u'children': [{u'children': [None],
    #                  'class': 'cell width-2 position-0',
    #                  u'column-size': 2,
    #                  u'roles': [u'Manager'],
    #                  u'type': u'group'},
    #                 {u'children': [{u'id': u'36759ad0c8114bb48467b858593b271f',
    #                                 u'tile-type': u'collective.cover.richtext',
    #                                 u'type': u'tile'}],
    #                  'class': 'cell width-14 position-2',
    #                  u'column-size': 14,
    #                  u'roles': [u'Manager'],
    #                  u'type': u'group'}],
    #   'class': 'row',
    #   u'type': u'row'}]
    #
    return rows


def make_row(*cols):
    # creates a cover row. Needs a list of columns (groups)
    return {
        'type': 'row',
        'children': cols
    }


def make_group(size=12, *tiles):
    #{"type": "group", "children":
    #     [
    #         {"tile-type": "collective.cover.richtext", "type": "tile", "id": "a42d3c2a88c8430da52136e2a204cf25"}
    #      ],
    #     "roles": ["Manager"],
    #     "column-size": 16}]

    return {
        'type': 'group',
        'roles': ['Manager'],
        'column-size': size,
        'children': tiles
    }


def noop(*args, **kwargs):
    """ no-op function to help with development of importers.
    It avoids pyflakes errors about not used variables.
    """
    # pprint(args)
    # pprint(kwargs)
    return


# def get_possible_title_for_layout(site, layout):
#     settings = parse_settings(layout.typesettings)
#     pass


def create_folder_at(site, location):
    parent = site

    for name in [x.strip() for x in location.split('/') if x.strip()]:
        if name not in parent.contentIds():
            parent = createAndPublishContentInContainer(
                parent,
                'Folder',
                title=name,
            )
        else:
            parent = parent[name]

    return parent


def create_cover_at(site, location, id='index_html', **kw):
    parent = site

    for name in [x.strip() for x in location.split('/') if x.strip()]:
        if name not in parent.contentIds():
            parent = createAndPublishContentInContainer(
                parent,
                'Folder',
                id=name,
                title=name,
            )
        else:
            parent = parent[name]

    cover = createAndPublishContentInContainer(
        parent,
        'collective.cover.content',
        id=id,
        **kw
    )
    cover.setLayout('no_title_cover_view')
    logger.debug("Created new cover at %s", cover.absolute_url(1))

    return cover


def create_plone_content(parent, **kw):
    type_ = kw.pop('type')
    content = createAndPublishContentInContainer(parent, type_, **kw)
    return content


def log_call(wrapped):
    def wrapper(*args, **kwargs):
        logger.debug("Calling %s", wrapped.__name__)
        return wrapped(*args, **kwargs)
    return wrapper


def render(path, options):
    tpl = PageTemplateFile(path, globals())
    ns = tpl.pt_getContext((), options)
    return tpl.pt_render(ns)


def render_accordion(payload):
    return render('templates/accordion.pt',
                          {'payload': payload,
                           'rand': lambda: str(random.randint(1, 10000))
                           }
                          )


def render_tabs(payload):
    return render('templates/tabs.pt',
                          {'payload': payload,
                           'rand': lambda: str(random.randint(1, 10000))
                           }
                          )

def pack_to_table(data):
    """ Convert a flat list of (k, v), (k, v) to a structured list
    """
    m = {
        'Item_name': 'Item',
        'Status': 'Status',
        'Web_links': 'Links',
    }
    visited = []
    rows = []
    acc = []
    for k, v in data:
        if k not in visited:
            visited.append(k)
            acc.append(v)
        else:
            rows.append(acc)
            visited = [k]
            acc = [v]

    rows.append(acc)
    return {'rows': rows, 'cols': [m[x] for x in visited]}


def localize(obj, site):
    """ Returns the path to an object, localized to the website"""
    path = obj.getPhysicalPath()
    site_path = site.getPhysicalPath()
    return '/' + '/'.join(path[len(site_path):])


def fix_inner_link(site, href):

    href = href.strip()

    # TODO: fix links like:
    # http://climate-adapt.eea.europa.eu/web/guest/uncertainty-guidance/topic2?p_p_id=56_INSTANCE_qWU5&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1#How+are+uncertainties+quantified%3F

    starters = [
        'http://climate-adapt.eea.europa.eu/',
        '../../../',
        '/web/guest/', '/'
    ]
    for path in starters:
        if href.startswith(path):
            href = href.replace(path, '/', 1)

    if href.startswith("#"):
        return href

    if "/viewmeasure" in href:
        acemeasure_id = get_param_from_link(href, 'ace_measure_id')
        obj = _get_imported_acemeasure(site, acemeasure_id)
        if obj:
            return localize(obj, site)

    if "/viewaceitem" in href:
        aceitem_id = get_param_from_link(href, 'aceitem_id')
        obj = _get_imported_aceitem(site, aceitem_id)
        if obj:
            return localize(obj, site)

    uuid = get_param_from_link(href, 'uuid')
    if uuid:
        return get_repofile_by_id(site, uuid)

    # some links are like: /documents/18/11231805/urban_ast_step0.png/38b047f5-65be-4fcd-bdd6-3bd9d52cd83d?t=1411119161497
    res = UUID_RE.search(href)
    if res:
        uuid = res.group()
        return get_repofile_by_id(site, uuid)
    else:
        logger.debug("Couldn't find proper equivalent link for %s", href)
        return href

    return href


_links = []

def write_links():
    global _links
    f = open('links.txt', 'a+')
    f.write("\n".join([x.encode('utf-8') for x in _links]))
    f.close()


def fix_links(site, text):
    global _links

    from lxml.html.soupparser import fromstring
    e = fromstring(text)

    for img in e.xpath('//img'):
        src = img.get('src')
        _links.append(src or '')

        image = get_image_from_link(site, src)

        if isinstance(image, str):
            pass
        else:
            if image is not None:
                url = localize(image, site) + "/@@images/image"
                logger.debug("Changed <img> link %s to %s", src, url)
                img.set('src', url)

    for a in e.xpath('//a'):
        href = a.get('href')
        _links.append(href or '')
        if href is not None:
            res = fix_inner_link(site, href)
            if not res:
                continue
            if href != res:
                if not isinstance(res, str):
                    res = localize(res, site)
                    #res = '/' + '/'.join(res.getPhysicalPath()[2:])
                logger.debug("Changed <a> link %s to %s", href, res)
                a.set('href', res)

    return lxml.html.tostring(e, encoding='unicode', pretty_print=True)


UUID_RE = re.compile(
    "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def get_repofile_by_id(context, id):
    if isinstance(id, str):
        id = id.strip()
        if not id:
            return None
    elif isinstance(id, (list, tuple)):
        id = id[0]

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(imported_ids=id)
    if not brains:
        logger.error("Could not find in catalog image by id %s", id)
        return

    if len(brains) != 1:
        logger.error("Multiple images found for", id)
        return

    return brains[0].getObject()


def get_param_from_link(text, param='uuid'):
    """ Extracts a query parameter from a link text
    """
    link = urllib.parse.urlparse(text)
    d = urllib.parse.parse_qs(link.query)
    if param in d:
        return d[param][0]


def get_image_from_link(site, link):
    """ Returns a Plone image object by extracting needed info from a link
    """

    # The logic is as followes:
    # images can be linked like: /something/?img_id=ZZZ  or /something/?uuid=ZZZ
    # or even /documents/18/11231805/urban_ast_step0.png/38b047f5-65be-4fcd-bdd6-3bd9d52cd83d?t=1411119161497
    # when imported from the database, they have been imported from two tables:
    # "image" and "dlfileentry"
    # The images are saved in the /repository/ folder in the Portal,
    # with an id of data.extension (for dlfileentry) and data.type_ (for images)
    # The dlfileentry also have the uuids, but they are sometimes linked
    # also with the largeimageid (or smallimageid), or data.name
    # a link can have either uuid or img_id

    if "@@images" in link:
        return link     # this is already a Plone link

    uuid = get_param_from_link(link, 'uuid')
    if uuid:
        return get_repofile_by_id(site, uuid)


    res = UUID_RE.search(link)
    if res:
        # some links are like: /documents/18/11231805/urban_ast_step0.png/38b047f5-65be-4fcd-bdd6-3bd9d52cd83d?t=1411119161497
        uuid = res.group()
        return get_repofile_by_id(site, uuid)

    image_id = get_param_from_link(link, 'img_id')
    if image_id:
        return get_repofile_by_id(site, image_id)

    #raise ValueError("Image not found for link: {0}".format(link))
    print(("Image not found for link: {0}".format(link)))
    return link     #TODO: put the error back


MAP_OF_OBJECTS = defaultdict(lambda:{})
ACEMEASURE_TYPES = ['eea.climateadapt.casestudy',
                    'eea.climateadapt.adaptationoption',]


def _get_imported_aceitem(site, id):
    catalog = getToolByName(site, 'portal_catalog')
    coll = MAP_OF_OBJECTS['aceitems']
    if len(coll) == 0:
        for pt in list(ACE_ITEM_TYPES.values()):
            brains = catalog.searchResults(portal_type=pt)
            for b in brains:
                obj = b.getObject()
                coll[obj._aceitem_id] = obj

    try:
        return coll[int(id)]
    except:
        logger.warning("Could not find aceitem with id %s", id)
        return


def _get_imported_aceproject(site, id):
    catalog = getToolByName(site, 'portal_catalog')
    pt = "eea.climateadapt.aceproject"
    coll = MAP_OF_OBJECTS['aceprojects']
    if len(coll) == 0:
        brains = catalog.search_results(portal_type=pt)
        for b in brains:
            obj = b.getObject()
            coll[obj._aceproject_id] = obj

    try:
        return coll[int(id)]
    except:
        logger.warning("Could not find aceproject with id %s", id)
        return


def _get_imported_acemeasure(site, id):
    catalog = getToolByName(site, 'portal_catalog')
    coll = MAP_OF_OBJECTS['acemeasures']
    if len(coll) == 0:
        for pt in ACEMEASURE_TYPES:
            brains = catalog.searchResults(portal_type=pt)
            for b in brains:
                obj = b.getObject()
                coll[obj._acemeasure_id] = obj

    try:
        return coll[int(id)]
    except:
        logger.warning("Could not find acemeasure with id %s", id)
        return


def get_relateditems(saobj, context):
    dbids = s2l(saobj.supdocs) or []
    files = [get_repofile_by_id(context, id) for id in dbids]
    util = getUtility(IIntIds, context=context)
    ids = [util.getId(f) for f in files]
    if ids:
        print(ids, saobj)

    return [RelationValue(id) for id in ids]


def _facetize(item, xml_filename):
    """ Make an item as faceted navigation
    """

    notify(FacetedWillBeEnabledEvent(item))
    alsoProvides(item, IFacetedNavigable)
    if not IDisableSmartFacets.providedBy(item):
        alsoProvides(item, IDisableSmartFacets)
    if not IHidePloneLeftColumn.providedBy(item):
        alsoProvides(item, IHidePloneLeftColumn)
    if not IHidePloneRightColumn.providedBy(item):
        alsoProvides(item, IHidePloneRightColumn)
    notify(FacetedEnabledEvent(item))

    import os.path
    fpath = os.path.join(os.path.dirname(__file__), 'faceted', xml_filename)
    with open(fpath) as f:
        xml = f.read()

    if not xml.startswith('<?xml version="1.0"'):
        raise ValueError('Please provide a valid xml file')

    environ = SnapshotImportContext(item, 'utf-8')
    importer = queryMultiAdapter((item, environ), IBody)
    if not importer:
        raise ValueError('No adapter found')

    importer.body = xml


def make_faceted(site, location, xmlfilename, layout):

    path = [x.strip() for x in location.split('/') if x.strip()]
    fname, parent_names = path[-1], path[:-1]

    parent = site
    for name in parent_names:
        if name not in parent.contentIds():
            parent = createAndPublishContentInContainer(
                parent,
                'Folder',
                title=name,
            )
        else:
            parent = parent[name]

    faceted = createAndPublishContentInContainer(parent, 'Folder', title=fname)
    _facetize(faceted, xmlfilename)

    if layout:
        faceted.setLayout(layout)

    logger.info("Created faceted folder at %s", faceted.absolute_url(1))

    return faceted


def _get_latest_version(session, saobj):
    """ Returns the latest version of a Journalarticle object

    Latest version means row where version is the biggest Decimal number
    """
    klass = saobj.__class__
    return session.query(klass).\
        filter_by(resourceprimkey=saobj.resourceprimkey).\
        order_by(klass.version.desc()).first()


def stamp_cover(cover, layout):
    cover._p_changed = True
    cover._imported_layout_id = layout.layoutid
    cover._imported_layout_uuid = layout.uuid_


# Search portlet has this info:
#  u'column-5': [(u'filteraceitemportlet_WAR_FilterAceItemportlet_INSTANCE_nY73',
#                 {'aceitemtype': 'NULL_VALUE',
#                  'anyOfThese': 'urban',
#                  'countries': 'NULL_VALUE',
#                  'datainfo_type': '2',
#                  'element': 'NULL_VALUE',
#                  'freetextAny': '2',
#                  'fuzziness': None,
#                  'impact': 'NULL_VALUE',
#                  'nrItemsPage': '10',
#                  'paging': '1',
#                  'portletSetupTitle_en_GB': 'Search results',
#                  'portletSetupTitle_en_US': 'Search results',
#                  'portletSetupUseCustomTitle': 'true',
#                  'sector': 'NULL_VALUE',
#                  'sortBy': 'RATING'})],

# Relevant portlet info (aka listing of content) has this info:
#  u'column-4': [(u'simplefilterportlet_WAR_SimpleFilterportlet_INSTANCE_bZn6',
#                 {'aceitemtype': 'INFORMATIONSOURCE',
#                  'anyOfThese': 'countr-area-urban',
#                  'countries': 'NULL_VALUE',
#                  'datainfo_type': '2',
#                  'element': 'NULL_VALUE',
#                  'freeparameter': '0',
#                  'freetextAny': '2',
#                  'fuzziness': None,
#                  'impact': 'NULL_VALUE',
#                  'lfrWapInitialWindowState': 'NORMAL',
#                  'lfrWapTitle': None,
#                  'nrItemsPage': '7',
#                  'portletSetupCss': '',
#                  'portletSetupShowBorders': 'true',
#                  'portletSetupTitle_en_GB': 'Information Portals',
#                  'portletSetupTitle_en_US': 'Information Portals',
#                  'portletSetupUseCustomTitle': 'true',
#                  'sector': 'NULL_VALUE',
#                  'sortBy': 'RATING'})],


# sortBy is one of:
# set(['NAME', 'NULL_VALUE', 'RATING'])

# impact is always null value

# sector is one of:
# set([None,
#      'AGRICULTURE',
#      'BIODIVERSITY',
#      'COASTAL',
#      'DISASTERRISKREDUCTION',
#      'FINANCIAL',
#      'HEALTH',
#      'INFRASTRUCTURE',
#      'MARINE',
#      'NULL_VALUE',
#      'WATERMANAGEMENT'])

# freeparameter is one of:
# set([None, '0', '1', '2', '3'])

# element is one of :
# set([None, 'MEASUREACTION', 'NULL_VALUE', 'OBSERVATIONS', 'VULNERABILITY'])

# Possible values for anyOfThese:
# set([None,
#      'Ast1-2',
#      'Ast1-3',
#      'Baltic Sea Region',
#      'Baltic sea region policy',
#      'MAPLAYER',
#      'NATP',
#      'NATPCZECHREPUBLIC',
#      'NATPREG',
#      'NATPREG NORTHERN_IRELAND',
#      'NATPREG SCOTLAND',
#      'NATPREG WALES',
#      'SETOFMAPS',
#      'adapt-meas-gen',
#      'agiculture',
#      'agriforestryresource',
#      'ast0-0',
#      'ast0-0city',
#      'ast0-1',
#      'ast0-2',
#      'ast0-3',
#      'ast1-0',
#      'ast1-0b',
#      'ast1-2',
#      'ast1-3',
#      'ast1-4',
#      'ast1-5',
#      'ast2',
#      'ast2-0',
#      'ast2-0city',
#      'ast2-1',
#      'ast2-2',
#      'ast2-3',
#      'ast2-4',
#      'ast2-5',
#      'ast3',
#      'ast3-0',
#      'ast3-2',
#      'ast4',
#      'ast4-0',
#      'ast4-0city',
#      'ast4-1',
#      'ast4-2',
#      'ast4-cbdatabase',
#      'ast5',
#      'ast5-0',
#      'ast5-0city',
#      'ast5-1',
#      'ast6',
#      'ast6-0',
#      'ast6-0city',
#      'ast6-2',
#      'atmosphere',
#      'atmosphereresource',
#      'baltic',
#      'biodiversity',
#      'biodiversityresource',
#      'bsr3-1',
#      'bsr3-2',
#      'bsr3-3',
#      'bsr4-1',
#      'bsr4-2',
#      'bsr4-3',
#      'coastal',
#      'coastalresource',
#      'countr-area-urban',
#      'cryosphereresource',
#      'disaster risk',
#      'disasterresource',
#      'financial',
#      'financialresource',
#      'health',
#      'healthresource',
#      'ice',
#      'infra-res',
#      'infrastructure',
#      'mapset-ast-obsscen',
#      'mapset-ast-vulnrisk',
#      'marineresource',
#      'obs-scen-atm',
#      'obs-scen-cry',
#      'obs-scen-gen',
#      'obs-scen-sea',
#      'obs-scen-ter',
#      'obs-scen-urb',
#      'obs-scen-wat',
#      'org1-global',
#      'org2-europe',
#      'urban',
#      'urbanresource',
#      'vuln-risk-gen',
#      'water',
#      'waterresource'])

# aceitemtype is on of:
# set(['ACTION',
#      'DOCUMENT',
#      'GUIDANCE',
#      'INDICATOR',
#      'INFORMATIONSOURCE',
#      'MAPGRAPHDATASET',
#      'MEASURE',
#      'NULL_VALUE',
#      'ORGANISATION',
#      'TOOL'])
#


# countries is one of:
# set([None,
#      'AT',
#      'BE',
#      'BG',
#      'CH',
#      'CY',
#      'DE',
#      'DK',
#      'EE',
#      'ES',
#      'FI',
#      'FR',
#      'GB',
#      'GR',
#      'HU',
#      'IE',
#      'IS',
#      'IT',
#      'LI',
#      'LT',
#      'LU',
#      'LV',
#      'MT',
#      'NL',
#      'NO',
#      'NULL_VALUE',
#      'PL',
#      'PT',
#      'RO',
#      'SE',
#      'SI',
#      'SK',
#      'TR'])
