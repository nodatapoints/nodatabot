"""
Text processing tests
"""
# pylint: disable = invalid-name
from unittest import TestCase
from common.reply_data import Text
from common.reply import processed_message_parts
from common.chatformat import parse_entities, italic, STYLE_HTML


class EntityParsingTest(TestCase):
    """
    Examine Text processing behaviour, in particular with
    the handling of utf-16 surrogate pairs in entity
    parsing
    """

    def runTest(self):
        """
        Feed some known problematic text through the parser
        """

        text, entities = parse_entities(f'Text:💬💬💬 {italic("Hello World")}')

        self.assertEqual(text, 'Text:💬💬💬 Hello World')
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].length, 11)
        self.assertEqual(entities[0].offset, 12)

        text, entities = parse_entities('<i></i>', STYLE_HTML)

        self.assertEqual(text, '')
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].length, 0)
        self.assertEqual(entities[0].offset, 0)

        text, entities = parse_entities('<i>Hello</i><code>World</code>', STYLE_HTML)

        self.assertEqual(text, 'HelloWorld')
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].length, 5)
        self.assertEqual(entities[0].offset, 0)
        self.assertEqual(entities[1].length, 5)
        self.assertEqual(entities[1].offset, 5)

        # ensure text transformation doesn't break anything

        text_obj, = processed_message_parts(Text(msg=text, entities=entities))
        text, entities = text_obj.msg, text_obj.entities

        self.assertEqual(text, 'HelloWorld')
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].length, 5)
        self.assertEqual(entities[0].offset, 0)
        self.assertEqual(entities[1].length, 5)
        self.assertEqual(entities[1].offset, 5)
