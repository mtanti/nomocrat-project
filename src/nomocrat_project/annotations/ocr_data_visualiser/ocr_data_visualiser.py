'''
OCR data visualisation related functions.
'''

import os
import shutil
import html
import PIL.Image
import PIL.ImageDraw
import tqdm
from nomocrat_project.annotations.common import (
    OCRData,
    Language,
)


##########################################################
def get_lang_select(
    box_x: int,
    box_y: int,
    selected: str,
    disabled: bool,
) -> str:
    '''
    Generate a <select> HTML list with the language of a transcription.

    :param box_x: The x-coordinate of the bounding box being described.
    :param box_y: The y-coordinate of the bounding box being described.
    :param selected: The language value to be selected.
    :param disabled: Whether to make the select list disabled/readonly.
    :return: The HTML code as a single string.
    '''
    disabled_part = ' disabled="disabled"' if disabled else ''
    def selected_part(lang_value: str) -> str:
        return ' selected="selected"' if lang_value == selected else ''
    return '\n'.join([
        f'<select id="lang_{box_x}_{box_y}"{disabled_part}>',
    ] + [
        f'            <option value="{lang.value}"{selected_part(lang.value)}>{lang.value}</option>'
        for lang in Language
    ] + [
        '        </select>',
    ])


##########################################################
def visualise_ocr_as_html(
    pages_path: str,
    data: OCRData,
    output_path: str,
    connect_to_server: bool = False,
) -> None:
    '''
    Generate images and HTML files that visualise the OCR data.

    :param pages_path: The path to the page images whose file names are referenced in the OCR data.
    :param data: The loaded OCR data (using
        `nomocrat_project.annotations.ocr_data_processor.import_ocr_data`).
    :param output_path: The path to the directory that will contain the visualisation files (will be
        created if not exists).
    :param connect_to_server: Whether to make the transcriptions come from a PHP server and add
        features to send requests to the server to modify the data as well.
    '''
    os.makedirs(os.path.join(output_path), exist_ok=True)

    if connect_to_server:
        shutil.copy(
            os.path.join(os.path.dirname(__file__), 'script.js'),
            os.path.join(output_path, 'script.js'),
        )
        shutil.copy(
            os.path.join(os.path.dirname(__file__), '_db_info.php'),
            os.path.join(output_path, '_db_info.php'),
        )
        shutil.copy(
            os.path.join(os.path.dirname(__file__), 'api.php'),
            os.path.join(output_path, 'api.php'),
        )
        shutil.copy(
            os.path.join(os.path.dirname(__file__), 'export.php'),
            os.path.join(output_path, 'export.php'),
        )

    shutil.copy(
        os.path.join(os.path.dirname(__file__), 'style.css'),
        os.path.join(output_path, 'style.css'),
    )

    dir_names = list[str]()
    for page_data in tqdm.tqdm(data.data):
        dir_name = f'{page_data.page.document_id}-{page_data.page.page_id}'
        os.makedirs(os.path.join(output_path, dir_name), exist_ok=True)
        dir_names.append(dir_name)

        page_fname = page_data.page.page_fname

        page_img_clean = PIL.Image.open(
            os.path.join(pages_path, page_fname)
        )
        page_img_dirty = page_img_clean.copy()
        page_draw = PIL.ImageDraw.Draw(page_img_dirty)

        box_fnames = list[str]()
        for (i, ocr_box) in enumerate(page_data.boxes, 1):
            page_draw.rectangle(
                (ocr_box.box.x, ocr_box.box.y, ocr_box.box.x2(), ocr_box.box.y2()),
                outline='red', width=3,
            )

            box_fname = f'{page_data.page.document_id}-{page_data.page.page_id}-{i}.jpg'
            page_img_clean.crop(
                (ocr_box.box.x, ocr_box.box.y, ocr_box.box.x2(), ocr_box.box.y2())
            ).save(
                os.path.join(output_path, dir_name, box_fname)
            )
            box_fnames.append(box_fname)

        page_img_dirty.save(
            os.path.join(output_path, dir_name, page_fname)
        )

        with open(os.path.join(output_path, dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            print(f'''\
<!DOCTYPE html>
<html lang="mt">
<head>
    <meta charset="UTF-8" />
    <title>{page_fname}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="description" content="" />
    <link rel="stylesheet" href="../style.css" />
''', file=f)
            if connect_to_server:
                print(f'''\
    <script src="../script.js"></script>
    <script type="text/javascript">setup('{page_fname}');</script>
''', file=f)
            print(f'''\
</head>
<body>
    <h1>{page_fname}</h1>
    <div class="section">
        <img src="{page_fname}" />
    </div>
''', file=f)

            for (box_fname, ocr_box) in zip(box_fnames, page_data.boxes):
                encoded_transcription = (
                    html.escape(ocr_box.transcription).replace('\n', ' NEWLINE ')
                )
                language = html.escape(ocr_box.language.value)
                box_x = ocr_box.box.x
                box_y = ocr_box.box.y
                print('''\
    <div class="section">
''', file=f)
                if connect_to_server:
                    print(f'''\
        {get_lang_select(box_x, box_y, selected='', disabled=False)}
        <div class="scrollableimg"><img src="{box_fname}" /></div>
        <textarea id="tran_{box_x}_{box_y}" class="transcription"></textarea>
        <br />
        <input type="button" id="save_{box_x}_{box_y}" value="Save" />
''', file=f)
                else:
                    print(f'''\
        {get_lang_select(box_x, box_y, selected=language, disabled=True)}
        <div class="scrollableimg"><img src="{box_fname}" /></div>
        <textarea id="tran_{box_x}_{box_y}" class="transcription" disabled="disabled">\
{encoded_transcription}</textarea>
''', file=f)
                print('''\
    </div>
''', file=f)

            print('''\
</body>
</html>
''', file=f)

    with open(os.path.join(output_path, 'index.html'), 'w', encoding='utf-8') as f:
        print('''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>OCR Data</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="description" content="" />
    <link rel="stylesheet" href="style.css" />
</head>
<body>
    <h1>OCR Data</h1>
    <ul>
''', file=f)
        for dir_name in dir_names:
            print(f'<li><a href="{dir_name}/index.html">{dir_name}</a></li>', file=f)
        print('''\
    </ul>
</body>
</html>
''', file=f)
