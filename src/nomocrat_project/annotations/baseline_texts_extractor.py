'''
Baseline text extraction related functions.
'''

import os
import re
import tqdm
import pypdf
from nomocrat_project.annotations.common import (
    PipelineData,
    BaselineData,
    BaselinePageData,
)


##########################################################
SPACES_RE = re.compile(' {2,}')

##########################################################
def extract_baseline_texts(
    docs_dir: str,
    pipeline_data: PipelineData,
) -> BaselineData:
    '''
    Extract text from the pages of the PDFs as indicated in a given pipline data.
    The extracted text will serve as a baseline for comparing against the OCR system.

    :param docs_dir: The path to the directory containing the documents. Must be PDFs.
    :param pipeline_data: The pipeline data to use as a reference for which documents and pages to
        extract text from.
    :return: The baseline texts.
    '''
    output = BaselineData(data=[])
    for doc in tqdm.tqdm(pipeline_data.data):
        path = os.path.join(docs_dir, f'{doc.page.document_id}.pdf')
        reader = pypdf.PdfReader(path)
        page = reader.pages[int(doc.page.page_id) - 1]
        page_text = page.extract_text(extraction_mode='layout')
        output.data.append(
            BaselinePageData(
                page=doc.page,
                texts=[
                    SPACES_RE.sub(' ', line).strip()
                    for line in page_text.split('\n')
                    if line.strip() != ''
                ],
            )
        )
    return output
