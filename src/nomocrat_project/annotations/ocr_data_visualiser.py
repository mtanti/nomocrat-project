'''
OCR data visualisation related functions.
'''

import os
import html
import PIL.Image
import PIL.ImageDraw
import tqdm
from nomocrat_project.annotations.common import OCRData


##########################################################
def visualise_as_html(
    pages_path: str,
    data: OCRData,
    output_path: str,
) -> None:
    '''
    Generate images and HTML files that visualise the OCR data.

    :param pages_path: The path to the page images whose file names are referenced in the OCR data.
    :param data: The loaded OCR data (using
        `nomocrat_project.annotations.ocr_data_processor.import_ocr_data`).
    :param output_path: The path to the directory that will contain the visualisation files (will be
        created if not exists).
    '''
    os.makedirs(os.path.join(output_path), exist_ok=True)

    with open(os.path.join(output_path, 'style.css'), 'w', encoding='utf-8') as f:
        print('''\
h1 {
    font-family: arial;
    font-size: 36pt;
}
.section {
    margin-top: 100px;
    padding: 10px;
    border-top: 5px black solid;
}
.label {
    font-family: arial;
    font-size: 10pt;
    font-weight: bold;
    border: 2px black solid;
    background-color: rgb(80%,80%,80%);
    border-radius: 5px;
    padding: 5px;
}
img {
    border: dashed 1pt black;
    margin-top: 10px;
}
.scrollableimg {
    width: 100%;
    height: 200px;
    overflow: scroll;
}
.transcription {
    font-family: 'courier new';
    font-size: 24pt;
    width: 100%;
    height: 200px;
}
a {
    font-family: arial;
    font-size: 18pt;
}
''', file=f)

    dir_names = list[str]()
    for page_data in tqdm.tqdm(data.data):
        dir_name = f'{page_data.page.document_id}-{page_data.page.page_id}'
        os.makedirs(os.path.join(output_path, dir_name), exist_ok=True)
        dir_names.append(dir_name)

        page_img_clean = PIL.Image.open(
            os.path.join(pages_path, page_data.page.page_fname)
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
            os.path.join(output_path, dir_name, page_data.page.page_fname)
        )

        with open(os.path.join(output_path, dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            print(f'''\
<!DOCTYPE html>
<html lang="mt">
<head>
    <meta charset="UTF-8" />
    <title>{page_data.page.page_fname}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="description" content="" />
    <link rel="stylesheet" href="../style.css" />
</head>
<body>
    <h1>{page_data.page.page_fname}</h1>
    <div class="section">
        <img src="{page_data.page.page_fname}" />
    </div>
''', file=f)

            for (box_fname, ocr_box) in zip(box_fnames, page_data.boxes):
                encoded_transcription = (
                    html.escape(ocr_box.transcription).replace('\n', ' NEWLINE ')
                )
                print(f'''\
    <div class="section">
        <span class="label">{ocr_box.language}</span>
        <div class="scrollableimg"><img src="{box_fname}" /></div>
        <textarea class="transcription">{encoded_transcription}</textarea>
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
