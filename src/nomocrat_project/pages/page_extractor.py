'''
Functions related to extracting pages from documents of various types.
'''

import os
import tempfile
import docx2pdf
import doc2docx
import pdf2image


##########################################################
def extract_pages(
    in_docs_dir: str,
    out_pages_dir: str,
) -> None:
    '''
    Extract all pages from all documents (*.pdf, *.docx, *.doc) in a directory as images (*.jpg).

    :param in_docs_dir: The path to the directory containing the documents.
    :param out_pages_dir: The path to the directory that will contain the page images (will be
        created if not exists).
    '''
    print('Extracting pages')
    os.makedirs(out_pages_dir, exist_ok=True)

    for doc_fname in os.listdir(in_docs_dir):
        print(' >', doc_fname)
        (doc_root, doc_ext) = os.path.splitext(doc_fname)
        doc_path = os.path.join(in_docs_dir, doc_fname)

        with tempfile.TemporaryDirectory() as tmp_dir:
            if doc_ext == '.doc':
                doc_path_ = os.path.join(tmp_dir, 'tmp.docx')
                doc2docx.convert(doc_path, doc_path_)
                doc_path = doc_path_
                doc_ext = '.docx'

            if doc_ext == '.docx':
                pdf_path = os.path.join(tmp_dir, 'tmp.pdf')
                docx2pdf.convert(doc_path, pdf_path)
            else:
                pdf_path = doc_path

            with open(pdf_path, 'rb') as f:
                pages = pdf2image.convert_from_bytes(f.read())
            for (page_num, page) in enumerate(pages, start=1):
                page.save(os.path.join(out_pages_dir, f'{doc_root}-{page_num:0>3d}.jpg'), 'JPEG')
