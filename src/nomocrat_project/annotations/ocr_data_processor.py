'''
OCR data processing related functions.
'''

import json
import os
import tqdm
from nomocrat_project.annotations.common import (
    BoundingBox, Language, OCRBox, Page, OCRPageData, OCRData
)


##########################################################
def import_ocr_data(
    path: str,
) -> OCRData:
    '''
    Load Label Studio OCR exported data that was exported via export -> JSON-min.

    :param path: The file path to the Label Studio exported OCR JSON file (JSON-min version).
    :return: The loaded data.
    '''
    errors: list[str] = []
    languages = {e.value: e for e in Language}

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ocr_data = list[OCRPageData]()
    for raw_page in tqdm.tqdm(data):
        new_errors: list[str] = []
        if 'label' not in raw_page:
            continue

        img_fname = os.path.basename(raw_page['ocr'])
        (root, ext) = os.path.splitext(img_fname)
        (_, document_id, page_id) = root.split('-')
        page_fname = f'{document_id}-{page_id}{ext}'
        page = Page(
            page_fname=page_fname,
            document_id=document_id,
            page_id=page_id,
        )

        ocr_boxes = list[OCRBox]()
        if not isinstance(raw_page['transcription'], list):
            raw_page['transcription'] = [raw_page['transcription']]
        assert len(raw_page['transcription']) == len(raw_page['label']), page_fname
        for (transcription, label) in zip(raw_page['transcription'], raw_page['label']):
            if len(label['rectanglelabels']) != 1:
                new_errors.append(f'Number of labels != 1 in {page_fname}.')
            if len(new_errors) == 0:
                ocr_box = OCRBox(
                    box=BoundingBox(
                        x=round(label['x']/100*label['original_width']),
                        y=round(label['y']/100*label['original_height']),
                        width=round(label['width']/100*label['original_width']),
                        height=round(label['height']/100*label['original_height']),
                    ),
                    transcription=transcription,
                    language=languages[label['rectanglelabels'][0]],
                )
                ocr_boxes.append(ocr_box)

        if len(new_errors) > 0:
            errors.extend(new_errors)
        else:
            ocr_boxes.sort(key=lambda item: (item.box.y, item.box.x))
            duplicate_xy = list[tuple[int, int]]()
            for i in range(0, len(ocr_boxes) - 1):
                curr_ocr_box = ocr_boxes[i].box
                next_ocr_box = ocr_boxes[i + 1].box
                if (curr_ocr_box.x, curr_ocr_box.y) == (next_ocr_box.x, next_ocr_box.y):
                    duplicate_xy.append((curr_ocr_box.x, curr_ocr_box.y))
            if len(duplicate_xy) > 0:
                for (x, y) in sorted(set(duplicate_xy)):
                    errors.append(f'Duplicate bounding box in {page_fname} at ({x}, {y}).')
            if len(errors) == 0:
                ocr_data.append(OCRPageData(
                    page=page,
                    boxes=ocr_boxes,
                ))

    if len(errors) > 0:
        raise ValueError('\n'.join(errors))

    ocr_data.sort(key=lambda item: item.page.page_fname)
    return OCRData(
        data=ocr_data,
    )
