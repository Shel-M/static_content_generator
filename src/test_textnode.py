import unittest

from htmlnode import LeafNode
from textnode import Block, BlockList, BlockType, TextNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

    def test_to_html(self):
        text = TextNode("test text node", "bold")
        self.assertEqual(
            str(text.to_html_node()),
            str(LeafNode(value="test text node", tag="b"))
        )

    def test_text_to_textnodes(self):
        nodes = TextNode.text_to_textnodes(
            "This is **text** with an *italic* word and a `code block` and an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and a [link](https://boot.dev)")
        expect = [
            TextNode("This is ", "text"),
            TextNode("text", "bold"),
            TextNode(" with an ", "text"),
            TextNode("italic", "italic"),
            TextNode(" word and a ", "text"),
            TextNode("code block", "code"),
            TextNode(" and an ", "text"),
            TextNode(
                "image",
                "image",
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"
            ),
            TextNode(" and a ", "text"),
            TextNode("link", "link", "https://boot.dev"),
        ]
        self.assertEqual(nodes, expect)

    def test_split_nodes_delimiter_simple(self):
        text = TextNode("**text** test node", "text")
        self.assertEqual(TextNode.split_nodes_delimiter([text], "**", "bold"),
                         [
                         TextNode("text", "bold"),
                         TextNode(" test node", "text"),
                         ])

    def test_split_nodes_delimiter_complex(self):
        text = TextNode("test **bold**** node** and **check extra**", "text")
        expect = [
            TextNode("test ", "text"),
            TextNode("bold", "bold"),
            TextNode(" node", "bold"),
            TextNode(" and ", "text"),
            TextNode("check extra", "bold")
        ]
        self.assertEqual(TextNode.split_nodes_delimiter(
            [text], "**", "bold"), expect)

    def test_split_nodes_images(self):
        text = [TextNode("This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)", "text")]
        split = TextNode.split_nodes_images(text)
        expect = [
            TextNode("This is text with an ", "text"),
            TextNode("image", text_type="image",
                     url="https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"),
            TextNode(" and ", "text"),
            TextNode("another", text_type="image",
                     url="https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png")
        ]
        self.assertEqual(split, expect)

    def test_split_nodes_links(self):
        text = [TextNode("This is text with an [link](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and [another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)", "text")]
        split = TextNode.split_nodes_links(text)
        expect = [
            TextNode("This is text with an ", "text"),
            TextNode("link", text_type="link",
                     url="https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"),
            TextNode(" and ", "text"),
            TextNode("another", text_type="link",
                     url="https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png")
        ]
        self.assertEqual(split, expect)

    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)"

        self.assertEqual(TextNode.extract_markdown_images(text),
                         [("image", "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"), ("another", "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png")])

    def test_extract_markdown_links(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        self.assertEqual(TextNode.extract_markdown_links(text),
                         [("link", "https://www.example.com"), ("another", "https://www.example.com/another")])


class TestBlockList(unittest.TestCase):
    def test_init(self):
        blocks = BlockList("""This is **bolded** paragraph

            This is another paragraph with *italic* text and `code` here
            This is the same paragraph on a new line

            * This is a list
            * with items """).blocks
        expect = [
            Block("This is **bolded** paragraph"),
            Block("""This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line"""),
            Block("""* This is a list
* with items""")
        ]

        self.assertEqual(str(blocks), str(expect))


class TestBlockType(unittest.TestCase):
    def test_from_block(self):
        blocks = BlockList("""This is **bolded** paragraph

            This is another paragraph with *italic* text and `code` here
            This is the same paragraph on a new line

            * This is a list
            * with items

            # Heading line

            >Quote 1
            >Quote 2

            1. First
            2. Secont (sic)
            3. Thirb c:""").blocks
        test = []
        for block in blocks:
            test.append(block.type)

        expect = [BlockType.paragraph, BlockType.paragraph, BlockType.unordered,
                  BlockType.heading, BlockType.quote, BlockType.ordered]
        self.assertListEqual(test, expect)


if __name__ == "__main__":
    unittest.main()
