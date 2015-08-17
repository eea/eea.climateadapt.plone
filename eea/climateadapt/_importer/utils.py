""" Importing utils
"""

import lxml.etree


def printe(e):
    """ debug function to easily see an etree as pretty printed xml"""
    print lxml.etree.tostring(e, pretty_print=True)


def s2l(text, separator=';'):
    """Converts a string in form: u'EXTREMETEMP;FLOODING;' to a list"""
    return filter(None, text.split(separator))


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
        v = filter(None, v.split(','))
        # if len(v) == 1:
        #     v = v[0]
        out[k] = v
    return out


def solve_dynamic_element(node):

    type_ = node.get('type')

    if type_ == 'image':
        imageid = node.xpath("dynamic-content/@id")
        return ('image', None, imageid)

    if type_ == 'text_area':
        return ('text',
                node.get('name'),
                node.xpath("dynamic-content/text()")
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

    import pdb; pdb.set_trace()


def solve_dynamic_content(node):
    return node.text
    #return ('text', None, node.text)


def solve_static_content(node):
    return node.text
    #return ('text', None, node.text)


SOLVERS = {
    'dynamic-element': solve_dynamic_element,
    'static-content': solve_static_content,
    'dynamic-content': solve_dynamic_content,
    #'static-element': solve_static_element,
}
