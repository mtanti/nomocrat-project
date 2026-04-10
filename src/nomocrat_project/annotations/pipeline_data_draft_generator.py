'''
Pipeline data draft generation related functions.
'''

import tqdm
import shapely
from nomocrat_project.annotations.common import (
    LayoutData,
    OCRData,
    PipelineData,
    PipelinePageData,
    OCRBox,
    LayoutLabel,
    PipelineChannel,
)
from typing import Optional


##########################################################
LABEL2CHANNEL: dict[LayoutLabel, Optional[PipelineChannel]] = {
    LayoutLabel.CAPTION: PipelineChannel.CAPTION,
    LayoutLabel.FOOTNOTE: PipelineChannel.FOOTNOTE,
    LayoutLabel.FORMULA: None,
    LayoutLabel.LIST_ITEM: PipelineChannel.TEXT,
    LayoutLabel.PAGE_FOOTER: None,
    LayoutLabel.PAGE_HEADER: None,
    LayoutLabel.PICTURE: None,
    LayoutLabel.SECTION_HEADER: PipelineChannel.TEXT,
    LayoutLabel.TABLE: None,
    LayoutLabel.TEXT: PipelineChannel.TEXT,
    LayoutLabel.TITLE: PipelineChannel.TEXT,
}
'''
Convert a layout label into a pipeline channel.
'''


##########################################################
def generate_pipeline_data_draft(
    ocr_data: OCRData,
    layout_data: LayoutData,
) -> PipelineData:
    '''
    Generate a draft pipeline data set showing what the target output should be when transcribing
    a whole page.

    This is done by:

    * joining the OCR and Layout data such that each OCR bounding box is given a
        layout label and only pages that are in both data sets are kept,
    * filtering out labels that are to be ignored (Picture, Table, Page-header, Page-footer,
        Formula),
    * grouping the filtered bounding boxes by label type into channels (Title, Section-header, Text,
        List-item are grouped together in a Text channel while Caption and Footnote are their own
        channels),
    * ordering the bounding boxes in each channel by y-coordinate followed by x-coordinate, and
    * generating a JSON formatted output mapping each page into a JSON document putting each channel
        as a separate list of texts together with their bounding box coordinates.

    The order of the bounding boxes is meant to be manually fixed afterwards (hence, draft).

    :param ocr_data: The loaded OCR data (using
        `nomocrat_project.annotations.ocr_data_processor.import_ocr_data`).
    :param layout_data: The loaded Layout data (using
        `nomocrat_project.annotations.layout_data_processor.import_layout_data`).
    :return: The draft pipeline data.
    '''
    fname2page = {doc.page.page_fname: doc.page for doc in ocr_data.data}
    ocr_fname2data = {doc.page.page_fname: doc.boxes for doc in ocr_data.data}
    layout_fname2data = {doc.page.page_fname: doc.polygons for doc in layout_data.data}
    fnames = sorted(set(ocr_fname2data)&set(layout_fname2data))
    result = list[PipelinePageData]()
    for fname in tqdm.tqdm(fnames):
        page = fname2page[fname]

        ocr_boxes = ocr_fname2data[fname]
        ocr_boxes_as_shapely = [
            shapely.box(box.box.x, box.box.y, box.box.x2(), box.box.y2())
            for box in ocr_boxes
        ]

        layout_polygons = layout_fname2data[fname]
        layout_polygons_as_shapely = [
            shapely.Polygon([(point.x, point.y) for point in polygon.polygon])
            for polygon in layout_polygons
        ]

        channelled_boxes = dict[PipelineChannel, list[OCRBox]]()
        for i in range(len(ocr_boxes)):
            # Find layout polygon with largest intersection area.
            max_intersection = 0.0
            max_intersection_index: int = -1
            for j in range(len(layout_polygons)):
                intersection_area = shapely.set_operations.intersection(
                    ocr_boxes_as_shapely[i],
                    layout_polygons_as_shapely[j],
                ).area
                relative_intersection_area = intersection_area/min(
                    ocr_boxes_as_shapely[i].area,
                    layout_polygons_as_shapely[j].area,
                )
                if relative_intersection_area > max_intersection:
                    max_intersection = relative_intersection_area
                    max_intersection_index = j
            if max_intersection <= 0.5:
                raise AssertionError(
                    f'Page {fname} has OCR box at ({ocr_boxes[i].box.x},{ocr_boxes[i].box.y})'
                    ' not intersecting significantly with any layout polygon.'
                )

            # Assign to OCR box the label in the intersecting layout polygon.
            label = layout_polygons[max_intersection_index].label
            channel = LABEL2CHANNEL[label]
            if channel is not None:
                if channel not in channelled_boxes:
                    channelled_boxes[channel] = []
                channelled_boxes[channel].append(ocr_boxes[i])

        for channel in channelled_boxes.keys():
            channelled_boxes[channel].sort(key=lambda box: (box.box.y, box.box.x))
        result.append(PipelinePageData(page=page, channels=channelled_boxes))

    return PipelineData(data=result)
