import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode("p", "Test P", None, None)
        self.assertEqual(
            str(node),
            "HTMLNode(tag(p), value(Test P), children(None), props(None))"
        )

    def test_prop_to_html(self):
        node = HTMLNode("p", "Test P", None, {
                        "href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(),
                         'href="https://www.google.com" target="_blank"')


class TestLeafNode(unittest.TestCase):
    def test_to_html_simple(self):
        node = LeafNode(tag="p", value="Paragraph Test")
        self.assertEqual(node.to_html(), "<p>Paragraph Test</p>")

    def test_to_html_complex(self):
        node = LeafNode(tag="a", value="Click me!", props={
                        "href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>')


class TestParentNode(unittest.TestCase):
    def test_to_html(self):
        node = ParentNode(
            tag="p",
            children=[
                LeafNode(tag="b", value="Bold text"),
                LeafNode("Normal text"),
                LeafNode(tag="i", value="italic text"),
                LeafNode("Normal text"),
            ],
        )
        self.assertEqual(node.to_html(
        ), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_from_markdown(self):
        test = ParentNode.from_markdown("""This is **bolded** paragraph

            This is another paragraph with *italic* text and `code` here
            This is the same paragraph on a new line

            * This is a list
            * with items

            # Heading line

            >Quote 1
            >Quote 2

            1. First
            2. Secont (sic)
            3. Thirb c:""").to_html()

        expect = """<div><p>This is <b>bolded</b> paragraph</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here
This is the same paragraph on a new line</p><ul><li>This is a list</li><li>with items</li></ul><h1>Heading line</h1><blockquote>>Quote 1
>Quote 2</blockquote><ol><li> First</li><li> Secont (sic)</li><li> Thirb c:</li></ol></div>"""

        self.assertEqual(test, expect)


if __name__ == "__main__":
    unittest.main()
