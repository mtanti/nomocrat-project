'''
OCR data visualisation related functions.
'''

import tqdm
from nomocrat_project.annotations.common import (
    OCRData,
    Language,
)


##########################################################
def convert_to_sql(
    data: OCRData,
) -> str:
    '''
    Convert OCR data to SQL in MySQL format.

    :param data: The loaded OCR data (using
        `nomocrat_project.annotations.ocr_data_processor.import_ocr_data`).
    :return: An SQL script as a string.
    '''
    language_to_id = {
        language: i
        for (i, language) in enumerate(Language, 1)
    }
    output = list[str]()
    output.extend([
        'CREATE DATABASE `nomocrat_ocr` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;',
        'USE `nomocrat_ocr`;',
        '',
        'CREATE TABLE `tbl_languages` (',
        '    `id` tinyint(3) UNSIGNED NOT NULL,',
        '    `language` varchar(20) COLLATE utf8_bin NOT NULL',
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;',
        'INSERT INTO `tbl_languages` (`id`, `language`) VALUES',
        ] + [
            f'    {"," if i > 0 else " "}({language_id}, \'{language.value}\')'
            for (i, (language, language_id)) in enumerate(language_to_id.items())
        ] + [
        ';',
        'ALTER TABLE `tbl_languages`',
        '    ADD PRIMARY KEY (`id`)',
        ';',
        '',
        'CREATE TABLE `tbl_pages` (',
        '    `id` int(10) UNSIGNED NOT NULL,',
        '    `page_fname` varchar(12) COLLATE utf8_bin NOT NULL,',
        '    `document_id` varchar(4) COLLATE utf8_bin NOT NULL,',
        '    `page_id` varchar(3) COLLATE utf8_bin NOT NULL',
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;',
        'ALTER TABLE `tbl_pages`',
        '    ADD PRIMARY KEY (`id`),',
        '    ADD UNIQUE KEY `page_fname` (`page_fname`)',
        ';',
        '',
        'CREATE TABLE `tbl_boxes` (',
        '    `id` int(10) UNSIGNED NOT NULL,',
        '    `page_id` int(10) UNSIGNED NOT NULL,',
        '    `x` smallint(5) UNSIGNED NOT NULL,',
        '    `y` smallint(5) UNSIGNED NOT NULL,',
        '    `width` smallint(5) UNSIGNED NOT NULL,',
        '    `height` smallint(5) UNSIGNED NOT NULL,',
        '    `transcription` text COLLATE utf8_bin NOT NULL,',
        '    `language_id` tinyint(3) UNSIGNED NOT NULL',
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;',
        'ALTER TABLE `tbl_boxes`',
        '    ADD PRIMARY KEY (`id`),',
        '    ADD KEY `page_id` (`page_id`),',
        '    ADD UNIQUE KEY `xy` (`page_id`, `x`, `y`)',
        ';',
        '',
        '',
    ])

    box_id = 1
    for (page_id, page_data) in enumerate(tqdm.tqdm(data.data), 1):
        encoded_page_fname = page_data.page.page_fname.replace('\'', '\\\'')
        encoded_document_id = page_data.page.document_id.replace('\'', '\\\'')
        encoded_page_id = page_data.page.page_id.replace('\'', '\\\'')
        output.append(
            'INSERT INTO `tbl_pages`('
            '`id`, `page_fname`, `document_id`, `page_id`'
            ') VALUES ('
            f'{page_id},'
            f' \'{encoded_page_fname}\','
            f' \'{encoded_document_id}\','
            f' \'{encoded_page_id}\''
            ');'
        )
        output.append(
            'INSERT INTO `tbl_boxes`('
            '`id`, `page_id`, `x`, `y`, `width`, `height`, `transcription`, `language_id`'
            ') VALUES'
        )
        for (i, ocr_box) in enumerate(page_data.boxes):
            encoded_transcription = (
                ocr_box.transcription
                .replace('\n', ' NEWLINE ')
                .replace('\'', '\\\'')
            )
            language_id = language_to_id[ocr_box.language]
            leading_char = ',' if i > 0 else ' '
            output.append(
                f'    {leading_char}('
                f'{box_id},'
                f' {page_id},'
                f' {ocr_box.box.x},'
                f' {ocr_box.box.y},'
                f' {ocr_box.box.width},'
                f' {ocr_box.box.height},'
                f' \'{encoded_transcription}\','
                f' {language_id}'
                ')'
            )
            box_id += 1
        output.append(';')
        output.append('')

    return '\n'.join(output)
