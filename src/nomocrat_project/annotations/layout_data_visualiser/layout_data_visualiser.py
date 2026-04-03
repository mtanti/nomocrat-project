'''
Layout data visualisation related functions.
'''

import os
import shutil
import PIL.Image
import PIL.ImageDraw
import tqdm
from nomocrat_project.annotations.common import LayoutData


##########################################################
COLOUR_LIST = [
    '#e6194b',
    '#3cb44b',
    '#ffe119',
    '#4363d8',
    '#f58231',
    '#911eb4',
    '#46f0f0',
    '#f032e6',
    '#bcf60c',
    '#fabebe',
    '#008080',
    '#e6beff',
    '#9a6324',
    '#fffac8',
    '#800000',
    '#aaffc3',
    '#808000',
    '#ffd8b1',
    '#000075',
    '#808080',
]


##########################################################
TRANSPARENT_HEX = '7f'


##########################################################
def visualise_layout_as_html(
    pages_path: str,
    data: LayoutData,
    output_path: str,
) -> None:
    '''
    Generate images and HTML files that visualise the layout data.

    :param pages_path: The path to the page images whose file names are referenced in the layout
        data.
    :param data: The loaded Layout data (using
        `nomocrat_project.annotations.layout_data_processor.import_layout_data`).
    :param output_path: The path to the directory that will contain the visualisation files (will be
        created if not exists).
    '''
    os.makedirs(os.path.join(output_path), exist_ok=True)

    shutil.copy(
        os.path.join(os.path.dirname(__file__), 'style.css'),
        os.path.join(output_path, 'style.css'),
    )

    label_colours = dict[str, str]()

    dir_names = list[str]()
    for page_data in tqdm.tqdm(data.data):
        dir_name = f'{page_data.page.document_id}-{page_data.page.page_id}'
        os.makedirs(os.path.join(output_path, dir_name), exist_ok=True)
        dir_names.append(dir_name)

        page_fname = page_data.page.page_fname

        page_img = PIL.Image.open(
            os.path.join(pages_path, page_fname)
        )
        page_draw = PIL.ImageDraw.Draw(page_img, 'RGBA')

        page_labels = set[str]()
        for polygon in page_data.polygons:
            label = polygon.label.value
            if label not in label_colours:
                if len(label_colours) == len(COLOUR_LIST):
                    raise Exception('Too many different labels. Only 20 colours supported.')
                label_colours[label] = COLOUR_LIST[len(label_colours)]
            page_labels.add(label)

            page_draw.polygon(
                [(point.x, point.y) for point in polygon.polygon],
                fill=f'{label_colours[label]}{TRANSPARENT_HEX}',
                outline=label_colours[label], width=3,
            )

        page_img.save(
            os.path.join(output_path, dir_name, page_fname)
        )

        with open(os.path.join(output_path, dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            print(f'''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>{page_fname}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="description" content="" />
    <link rel="stylesheet" href="../style.css" />
    <script type="text/javascript">
        const data = {page_data.model_dump_json()};
        function showJSON(i) {{
            document.getElementById('json').value = JSON.stringify(data['polygons'][i], null, 4);
        }}
    </script>
</head>
<body>
    <h1>{page_fname}</h1>
    <div>
        <table>
            <tr>
                <th>Colour</th>
                <th>Label</th>
            </tr>
''', file=f)
            for label in sorted(page_labels):
                print(f'''\
            <tr>
                <td style="background-color: {label_colours[label]};">&nbsp;</td>
                <td>{label}</td>
            </tr>
''', file=f)
            print(f'''\
        </table>
        <textarea id="json" cols="30" rows="8"></textarea>
    </div>
    <div class="scrollableimg"><img src="{page_fname}" usemap="#map" /></div>
    <map name="map">
''', file=f)
            for (i, polygon) in enumerate(page_data.polygons):
                print(f'''\
        <area shape="poly" coords="{','.join(str(x) for p in polygon.polygon for x in [p.x, p.y])}" onclick="showJSON({i})" />
''', file=f)
            print('''\
    </map>
</body>
</html>
''', file=f)

    with open(os.path.join(output_path, 'index.html'), 'w', encoding='utf-8') as f:
        print('''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Layout Data</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="description" content="" />
    <link rel="stylesheet" href="style.css" />
</head>
<body>
    <h1>Layout Data</h1>
    <ul>
''', file=f)
        for dir_name in dir_names:
            print(f'<li><a href="{dir_name}/index.html">{dir_name}</a></li>', file=f)
        print('''\
    </ul>
</body>
</html>
''', file=f)
