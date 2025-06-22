'''
OCR data processing related functions.
'''

import json
import os
import tqdm
import shapely
from nomocrat_project.annotations.common import (
    Point, LayoutLabel, LayoutPolygon, Page, LayoutPageData, LayoutData
)


##########################################################
def import_layout_data(
    path: str,
) -> LayoutData:
    '''
    Load Label Studio layout exported data that was exported via export -> JSON-min.

    :param path: The file path to the Label Studio exported layout JSON file (JSON-min version).
    :return: The loaded data.
    '''
    labels = {e.value: e for e in LayoutLabel}

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    layout_data = list[LayoutPageData]()
    for raw_page in tqdm.tqdm(data):
        img_fname = os.path.basename(raw_page['image'])
        (root, ext) = os.path.splitext(img_fname)
        (_, document_id, page_id) = root.split('-')
        page_fname = f'{document_id}-{page_id}{ext}'
        page = Page(
            page_fname=page_fname,
            document_id=document_id,
            page_id=page_id,
        )

        layout_polygons = list[LayoutPolygon]()
        for ply in raw_page['ply']:
            assert ply['closed']
            assert len(ply['points']) >= 3
            assert len(ply['polygonlabels']) == 1
            layout_polygon = LayoutPolygon(
                polygon=[
                    Point(
                        x=round(point[0]/100*ply['original_width']),
                        y=round(point[1]/100*ply['original_height']),
                    )
                    for point in ply['points']
                ],
                label=labels[ply['polygonlabels'][0]],
            )
            layout_polygons.append(layout_polygon)

        polys = [
            shapely.Polygon([(point.x, point.y) for point in layout_polygon.polygon])
            for layout_polygon in layout_polygons
        ]
        for poly in polys:
            assert poly.is_simple
        for i in range(0, len(polys) - 1):
            for j in range(i + 1, len(polys)):
                assert not polys[i].intersects(polys[j])

        layout_polygons.sort(key=lambda item: (item.get_leftmost_x()//10, item.get_topmost_y()//10))
        layout_data.append(LayoutPageData(
            page=page,
            polygons=layout_polygons,
        ))

    layout_data.sort(key=lambda item: item.page.page_fname)
    return LayoutData(
        data=layout_data,
    )
