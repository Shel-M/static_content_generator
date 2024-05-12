from typing import Dict


class HTMLNode:
    def __init__(
        self,
        tag: (str | None) = None,
        value: (str | None) = None,
        children: (list["LeafNode"] | list["ParentNode"] | None) = None,
        props: (Dict | None) = None
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self) -> str:
        return f"HTMLNode(tag({self.tag}), \
value({self.value}), \
children({self.children}), \
props({self.props}))"

    def to_html(self): raise NotImplementedError

    def props_to_html(self) -> str:
        html = ""
        if self.props:
            for key in self.props:
                html = " ".join((html, f'{key}="{self.props[key]}"'))
        return html.strip()


class LeafNode(HTMLNode):
    def __init__(
        self,
        value: str,
        tag=None,
        props: (Dict | None) = None
    ) -> None:
        super().__init__(tag=tag, value=value, props=props)

    def __repr__(self) -> str:
        return f"LeafNode(tag({self.tag}), \
value({self.value}), \
children({self.children}), \
props({self.props}))"

    def to_html(self) -> str:
        if self.tag:
            html = f"<{self.tag} {self.props_to_html()}".strip() + ">"
            html += f"{self.value}</{self.tag}>"
            return html
        return self.value


class ParentNode(HTMLNode):
    from textnode import Block

    def __init__(
            self,
            tag: str,
            children: (list["ParentNode"] | list["LeafNode"] | None) = None,
            props: (Dict | None) = None) -> None:
        super().__init__(tag=tag, children=children, props=props)

    def __repr__(self) -> str:
        return f"ParentNode(tag({self.tag}), \
value({self.value}), \
children({self.children}), \
props({self.props}))"

    def to_html(self):
        if not self.tag:
            raise ValueError("No tag provided!")
        if not self.children:
            raise ValueError("No children provided!")

        html = f"<{self.tag} {self.props_to_html()}".strip() + ">"
        for child in self.children:
            html += child.to_html()
        html += f"</{self.tag}>"
        return html

    def extract_title(self) -> "LeafNode":
        if not len(self.children):
            return None
        for child in self.children:
            if child.tag == "h1":
                return child.children[0].value
            elif len(child.children):
                return child.extract_title()
            else:
                return None

    @staticmethod
    def from_block(block: Block) -> "ParentNode":
        from textnode import BlockType, TextNode

        node = ParentNode("", [])
        if block.type == BlockType.paragraph:
            node.tag = "p"
        elif block.type == BlockType.heading:
            node.tag = f"h{block.header_level()}"
            block.value = block.value.lstrip("#").lstrip()
        elif block.type == BlockType.code:
            node.tag = "pre"
            node.children.append(LeafNode(tag="code", value=block.value))
            return node
        elif block.type == BlockType.quote:
            node.tag = "blockquote"
        elif block.type == BlockType.unordered:
            node.tag = "ul"
            for line in block.value.splitlines():
                list_item = ParentNode(tag="li", children=[])
                for tnode in TextNode.text_to_textnodes(line[2:]):
                    list_item.children.append(tnode.to_html_node())
                node.children.append(list_item)
            return node
        elif block.type == BlockType.ordered:
            node.tag = "ol"
            for line in block.value.splitlines():
                list_item = ParentNode(tag="li", children=[])
                for tnode in TextNode.text_to_textnodes(line[2:]):
                    list_item.children.append(tnode.to_html_node())
                node.children.append(list_item)
            return node

        nodes = list(map(lambda n: n.to_html_node(),
                         TextNode.block_to_textnodes(block)))
        node.children.extend(nodes)
        return node

    @staticmethod
    def from_markdown(markdown: str) -> "ParentNode":
        from textnode import BlockList

        parent = ParentNode("div", [])

        blocklist = BlockList(markdown)
        for block in blocklist.blocks:
            parent.children.append(ParentNode.from_block(block))

        return parent
