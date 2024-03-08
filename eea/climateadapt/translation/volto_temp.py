""" WIP Translate for volto
"""

from eea.climateadapt.translation.utils import (
    get_site_languages,
)
from eea.climateadapt.asynctasks.utils import get_async_service

from .core import (
    create_translation_object,
    execute_translate_async,
)
import logging

logger = logging.getLogger("eea.climateadapt")


def translate_volto_html(html, en_obj, http_host):
    obj = en_obj
    options = {}
    options["obj_url"] = en_obj.absolute_url()
    options["uid"] = en_obj.UID()
    options["http_host"] = http_host
    options["is_volto"] = True
    options["html_content"] = html

    request_vars = {
        # 'PARENTS': obj.REQUEST['PARENTS']
    }

    if "/en/" in en_obj.absolute_url():
        # run translate FULL (all languages)
        for language in get_site_languages():
            if language == "en":
                continue

            create_translation_object(en_obj, language)
            async_service = get_async_service()
            queue = async_service.getQueues()[""]
            async_service.queueJobInQueue(
                queue,
                ("translate",),
                execute_translate_async,
                obj,
                options,
                language,
                request_vars,
            )
