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
