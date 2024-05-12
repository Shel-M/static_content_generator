from enum import Enum
import re
from htmlnode import LeafNode


class TextNode:
    def __init__(
            self,
            text: str,
            text_type: str,
            url: (str | None) = None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)

    def __repr__(self) -> str:
        return f"TextNode('{self.text}', {self.text_type}, {self.url})"

    def to_html_node(self) -> LeafNode:
        type = self.text_type
        leaf = LeafNode(value=self.text)

        if type == "bold":
            leaf.tag = "b"
        elif type == "italic":
            leaf.tag = "i"
        elif type == "code":
            leaf.tag = "code"
        elif type == "link":
            leaf.tag = "a"
            leaf.props = {"href": self.url}
        elif type == "image":
            leaf.tag = "img"
            leaf.value = ""
            leaf.props = {"src": self.url, "alt": self.text}
        elif type != "text":
            raise Exception("Invalid text type to convert.")

        return leaf

    @staticmethod
    def block_to_textnodes(block: "Block") -> list["TextNode"]:
        if block.type in [BlockType.unordered, BlockType.ordered]:
            textnodes = []
            for line in block.value.splitlines():
                textnodes.extend(TextNode.text_to_textnodes(line))
            print()
            print(block)
            print()
            print(textnodes)
            print()
            return textnodes

        return TextNode.text_to_textnodes(block.value)

    @staticmethod
    def text_to_textnodes(text: str) -> list["TextNode"]:
        new = TextNode.split_nodes_delimiter(
            [TextNode(text, "text")], "**", "bold")
        new = TextNode.split_nodes_delimiter(new, "*", "italic")
        new = TextNode.split_nodes_delimiter(new, "`", "code")

        new = TextNode.split_nodes_images(new)
        new = TextNode.split_nodes_links(new)

        return new

    @staticmethod
    def split_nodes_delimiter(
            old: list["TextNode"],
            delimiter: str,
            text_type: str) -> list["TextNode"]:
        new = []
        for node in old:
            if node.text_type != "text":
                new.append(node)
                continue
            # This is text with a `code block` word `Code 2`
            t: str = node.text
            parts: list[TextNode] = []
            while t.find(delimiter) >= 0:
                p = t.split(delimiter, maxsplit=2)
                if len(p) < 3:
                    raise Exception("Invalid markdown")
                if len(p[0]):
                    parts.append(TextNode(p[0], "text"))
                parts.append(TextNode(p[1], text_type))
                t = p[2]
            if len(t):
                parts.append(TextNode(t, "text"))
            new.extend(parts)
        return new

    @staticmethod
    def split_nodes_images(old: list["TextNode"]) -> list["TextNode"]:
        new = []
        for node in old:
            if node.text_type != "text":
                new.append(node)
                continue
            images = TextNode.extract_markdown_images(node.text)
            text = node.text
            for image in images:
                image_start = text.find(image[0])-2
                image_end = image_start + 2 + \
                    len(image[0]) + 2 + len(image[1]) + 1

                if image_start:  # image_start isn't first char
                    new.append(TextNode(text[:image_start], "text"))
                new.append(
                    TextNode(text=image[0], text_type="image", url=image[1]))
                text = text[image_end:]
            if len(text) > 0:
                new.append(TextNode(text, "text"))

        return new

    @staticmethod
    def split_nodes_links(old: list["TextNode"]) -> list["TextNode"]:
        new = []
        for node in old:
            if node.text_type != "text":
                new.append(node)
                continue
            links = TextNode.extract_markdown_links(node.text)
            text = node.text
            for link in links:
                link_start = text.find(link[0])-1
                link_end = link_start + 1 + len(link[0]) + 2 + len(link[1]) + 1

                if link_start:  # image_start isn't first char
                    new.append(TextNode(text[:link_start], "text"))
                new.append(
                    TextNode(text=link[0], text_type="link", url=link[1]))
                text = text[link_end:]
            if len(text) > 0:
                new.append(TextNode(text, "text"))

        return new

    @staticmethod
    def extract_markdown_images(text: str) -> list[tuple[str, str]]:
        return re.findall(r"!\[(.*?)\]\((.*?)\)", text)

    @staticmethod
    def extract_markdown_links(text: str) -> list[tuple[str, str]]:
        return re.findall(r"\[(.*?)\]\((.*?)\)", text)


class Block:
    def __init__(self, value: str):
        self.value = value
        self.type = BlockType.from_block_value(value)

    def __repr__(self):
        return f"Block(value: {self.value}, type: {self.type})"

    def header_level(self) -> int:
        if not self.type == BlockType.heading:
            raise ValueError("Not a heading type block")

        level = len(self.value)
        level -= len(self.value.lstrip("#").lstrip())+1
        return level


class BlockList:
    def __init__(self, text: str):
        self.blocks = self.from_markdown(text)

    @staticmethod
    def from_markdown(markdown: str) -> list[Block]:
        blocks = []
        tmp_block = ""
        for line in markdown.split('\n'):
            if len(line):
                tmp_block = "\n".join((tmp_block, line.strip()))
            elif tmp_block:
                blocks.append(Block(tmp_block.lstrip()))
                tmp_block = ""
        if len(tmp_block):
            blocks.append(Block(tmp_block.lstrip()))
            tmp_block = ""
        return blocks


class BlockType(Enum):
    paragraph = "paragraph"
    heading = "heading"
    code = "code"
    quote = "quote"
    unordered = "unordered"
    ordered = "ordered"

    @staticmethod
    def from_block(block: Block):
        BlockType.from_block_value(block.value)

    @staticmethod
    def from_block_value(value: str):
        blocklines = value.splitlines()
        if re.search("^#+ ", value):
            return BlockType.heading
        if value.startswith("```") and value.endswith("```"):
            return BlockType.code
        if all(map(lambda s: s.startswith(">"), blocklines)):
            return BlockType.quote
        if all(map(
                lambda s: s.startswith("* ") or s.startswith("- "),
                blocklines)):
            return BlockType.unordered

        i = 0
        state = True
        for line in blocklines:
            i += 1
            if not line.startswith(f"{i}. "):
                state = False
                break
        if state:
            return BlockType.ordered

        return BlockType.paragraph
