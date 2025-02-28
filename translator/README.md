# Translation workflow

- A trigger condition causes Plone content to be flagged for translation
  - we use content rules
    - object modified if published
    - object is published
- Plone queues job in Redis with:
  - canonical object path
- Worker picks up this job and triggers multiple Plone views that set up the translated object for each language
  - `@@setup_translation`, gets executed for one languages
- This worker then calls a view in Plone which calls eTranslation
  - the view creates the HTML representation of object for eTranslation
- eTranslation calls to Plone, which queues a job to the translator
  - this job has the content translated
  - the translator then calls Plone to save the translated content

## Trigger conditions

- manually calling for translation on an object
- manually calling for recursive translation on a folder
