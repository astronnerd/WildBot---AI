from llama_index.core.readers.base import BaseReader
from llama_index.core import Document
import pymupdf4llm
import re
from src.utils.logger import get_logger
import os

logger = get_logger(__name__)

class PDF4LLMReader(BaseReader):
    def load_data(self, file, extra_info=None):
        docs = []
        logger.debug(f"Parsing file {file}")
        pages_md_text = pymupdf4llm.to_markdown(file, page_chunks=True)
        parent_ref_doc_id = re.sub("\s+", "_", str(pages_md_text[0]['metadata']['title']))
        # load_data returns a list of Document objects
        for page_md_text in pages_md_text:
            # we are making document at page level that is why needed parent doc id for chunk contextual information
            docs.append(Document(doc_id = re.sub("\s+", "_", parent_ref_doc_id + "_page_"+str(page_md_text['metadata']['page'])),
                                text=page_md_text['text'], 
                    metadata = {"parent_ref_doc_id": parent_ref_doc_id,
                                "page_num": page_md_text['metadata']['page'], 
                                "doc_title": page_md_text['metadata']['title']}, 
                                excluded_embed_metadata_keys=["doc_title", "page_num", "parent_ref_doc_id"],
                                excluded_llm_metadata_keys=["doc_title", "page_num", "parent_ref_doc_id"]))
        return docs