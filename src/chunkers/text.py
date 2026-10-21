import uuid

class TextChunker:

    def build_chunks(self, file_path, max_chunk_size):

        with open(file_path, "r") as file:
            source = file.read()

        start = 0
        end = max_chunk_size

        while start < len(source):

            check = source[start:end]

            if "\n" in check:
                end = source[:end].rindex("\n") + 1
            elif "." in check:
                end = source[:end].rindex(".") + 1
            elif "," in check:
                end = source[:end].rindex(",") + 1
            elif " " in check:
                end = source[:end].rindex(" ") + 1

            text = source[start:end]

            yield ({
                "id": f"{file_path}{start}",
                "file_path": str(file_path),
                "first_character_index": start,
                "last_character_index": end,
                "text": text
            })

            start = end
            end += max_chunk_size

