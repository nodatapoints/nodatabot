"""
Text processing tests
"""
# pylint: disable = invalid-name
from unittest import TestCase
from common.reply_data import Text
from common.reply import processed_message_parts
from common.chatformat import parse_entities, italic, STYLE_HTML, STYLE_MD, STYLE_PARA, STYLE_BACKEND, render


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


class EntityTransformationTest(TestCase):
    """
    Check chatformat's utilities to transform different
    markup encodings
    """
    def runTest(self):
        """ test """
        styles = {
            STYLE_HTML: '<code> hello </code><i>test</i><code>2</code><i>b</i><b>i</b>',
            STYLE_MD: '` hello `_test_`2`_b_*i*',
            STYLE_BACKEND: '!§![c hello !§!]c!§![itest!§!]i!§![c2!§!]c!§![ib!§!]i!§![bi!§!]b',
            STYLE_PARA: 'm§ hello §i§test§m§2§i§b§b§i§'
        }

        for input_style, input_text in styles.items():
            text, style = render(input_text, input_style)
            self.assertEqual(styles[style], text, msg=f'Transforming from {input_style} to {style}')

        for input_style, input_text in styles.items():
            if input_style == STYLE_HTML:
                continue

            for target_style, target_text in styles.items():
                if input_style == STYLE_BACKEND and target_style not in (STYLE_HTML, STYLE_BACKEND):
                    continue
                text, style = render(input_text, input_style, target_style)
                self.assertEqual(target_style, style)
                self.assertEqual(target_text, text, msg=f'Transforming from {input_style} to {style}')
