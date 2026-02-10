<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

ini_set('default_charset', 'UTF-8');
mb_internal_encoding('UTF-8');
mb_http_output('UTF-8');

include('_db_info.php');
$db = new PDO('mysql:host='.$dbHost.';dbname='.$dbName.';charset=utf8', $dbUser, $dbPassword);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$db->setAttribute(PDO::ATTR_ORACLE_NULLS, PDO::NULL_NATURAL);

$stmt = $db->prepare('
    SELECT
        `tbl_pages`.`page_fname` AS `page_fname`,
        `tbl_pages`.`document_id` AS `document_id`,
        `tbl_pages`.`page_id` AS `page_id`,
        `tbl_boxes`.`x` AS `x`,
        `tbl_boxes`.`y` AS `y`,
        `tbl_boxes`.`width` AS `width`,
        `tbl_boxes`.`height` AS `height`,
        `tbl_boxes`.`transcription` AS `transcription`,
        `tbl_languages`.`language` AS `language`
    FROM `tbl_pages`
        INNER JOIN `tbl_boxes` ON `tbl_boxes`.`page_id` = `tbl_pages`.`id`
        INNER JOIN `tbl_languages` ON `tbl_boxes`.`language_id` = `tbl_languages`.`id`
    ORDER BY
        `page_fname` ASC, `x` ASC, `y` ASC
    ;
');
$stmt->execute();

$result = array('data' => array());
$currPageDoc = null;
$lastPageId = 0;
$dataRows = $stmt->fetchAll(PDO::FETCH_ASSOC);

for ($i = 0; $i < count($dataRows); $i++) {
    if ($dataRows[$i]['page_id'] != $lastPageId) {
        if ($currPageDoc != null) {
            $result['data'][] = $currPageDoc;
        }
        $currPageDoc = array(
            'page' => array(
                'page_fname' => $dataRows[$i]['page_fname'],
                'document_id' => $dataRows[$i]['document_id'],
                'page_id' => $dataRows[$i]['page_id'],
            ),
            'boxes' => array(),
        );
        $lastPageId = $dataRows[$i]['page_id'];
    }
    $currPageDoc['boxes'][] = array(
        'box' => array(
            'x' => intval($dataRows[$i]['x']),
            'y' => intval($dataRows[$i]['y']),
            'width' => intval($dataRows[$i]['width']),
            'height' => intval($dataRows[$i]['height']),
        ),
        'transcription' => $dataRows[$i]['transcription'],
        'language' => $dataRows[$i]['language'],
    );
}

$output = json_encode(
    $result,
    JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE
);

header('Content-Type: application/json');
header('Content-disposition: attachment; filename="ocr_data.json"');
echo $output;
