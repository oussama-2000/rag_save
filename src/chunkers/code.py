from tree_sitter import Parser, Language
import tree_sitter_python as py_lang
import uuid

class CodeChunker:
    def __init__(self, max_chunk_size):
        self.max_chunk_size = max_chunk_size
        self.source = None
        self.language = Language(py_lang.language())
        self.parser = Parser(self.language)
        self.tree = None
        

    def build_tree(self, file_path):
        with open(file_path, "r") as file:
            self.source = file.read().encode()

        tree = self.parser.parse(self.source)
        self.tree = tree

    def byte_to_char_index(self, byte_index):
        return len(self.source[:byte_index].decode())
    
    def extract_nodes(self, node):
        nodes = []

        for child in node.named_children:

            text = self.source[child.start_byte: child.end_byte].decode()
            size = len(text)

            if size <= self.max_chunk_size:
                start = self.byte_to_char_index(child.start_byte)
                end = self.byte_to_char_index(child.end_byte)

                nodes.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
            else:
                nodes.extend(
                    self.extract_nodes(child)
                )

        return nodes

    def build_chunks(self, file_path):

        self.build_tree(file_path)
        nodes = self.extract_nodes(self.tree.root_node)

        i = 0
        while i < len(nodes):
            buffer = nodes[i]['text']
            start = nodes[i]['start']
            end = nodes[i]['end']

            j = i + 1
            while j < len(nodes):

                check = len(buffer + nodes[j]['text'])

                if check >= self.max_chunk_size - 1:
                    break

                buffer += " " + nodes[j]['text']
                end = nodes[j]['end']
                j += 1

            yield ({
                "id": f"{file_path}{start}",
                "file_path": file_path.name,
                "first_character_index": start,
                "last_character_index": end,
                "text": buffer
            })

            i = j



# chunker = CodeChunker(200)

# chunks1 = chunker.build_chunks("src/chunkers/code.py")
# # chunks2 = chunker.build_chunks("src/chunkers/code.py")
# print(chunks1)

