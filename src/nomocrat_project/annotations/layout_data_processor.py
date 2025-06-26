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
    errors: list[str] = []
    labels = {e.value: e for e in LayoutLabel}

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    layout_data = list[LayoutPageData]()
    for raw_page in tqdm.tqdm(data):
        new_errors: list[str] = []

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
            if not ply['closed']:
                new_errors.append(f'Open polygon in {page_fname}.')
            if len(ply['points']) < 3:
                new_errors.append(f'Polygon with < 3 vertices in {page_fname}.')
            if len(ply['polygonlabels']) != 1:
                new_errors.append(f'Number of labels != 1 in {page_fname}.')
            if len(new_errors) == 0:
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

        # Check for geometric errors.
        polys = [
            shapely.Polygon([(point.x, point.y) for point in layout_polygon.polygon])
            for layout_polygon in layout_polygons
        ]
        if any(not poly.is_simple for poly in polys):
            new_errors.append(f'Non-simple polygon in {page_fname}.')
        if any(
            polys[i].intersects(polys[j])
            for i in range(0, len(polys) - 1)
            for j in range(i + 1, len(polys))
        ):
            new_errors.append(f'Intersecting polygons in {page_fname}.')

        if len(new_errors) > 0:
            errors.extend(new_errors)
        else:
            layout_polygons.sort(
                key=lambda item: (item.get_leftmost_x()//10, item.get_topmost_y()//10)
            )
            layout_data.append(LayoutPageData(
                page=page,
                polygons=layout_polygons,
            ))

    if len(errors) > 0:
        raise Exception('\n'.join(errors))

    layout_data.sort(key=lambda item: item.page.page_fname)
    return LayoutData(
        data=layout_data,
    )
