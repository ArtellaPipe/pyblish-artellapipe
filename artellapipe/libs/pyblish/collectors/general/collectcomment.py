import pyblish.api


class CollectComment(pyblish.api.ContextPlugin):

    label = 'Collect Comment'
    order = pyblish.api.CollectorOrder

    def process(self, context):

        context.data['comment'] = ''
