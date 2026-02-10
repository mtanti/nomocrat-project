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

try {
    if (!array_key_exists('submit', $_REQUEST)) {
        throw new Exception('Can\'t use API without a submit.');
    }
    $submit = $_REQUEST['submit'];
    
    /*******************************/
    if ($submit == 'read') {
        if (!array_key_exists('page_fname', $_REQUEST)) {
            throw new Exception('Missing page_fname in request.');
        }
        $pageFName = $_REQUEST['page_fname'];
        if (mb_strlen($pageFName) != 12) {
            throw new Exception('page_fname is not the right length.');
        }
        
        $stmt = $db->prepare('
            SELECT
                `tbl_boxes`.`x` AS `box_x`,
                `tbl_boxes`.`y` AS `box_y`,
                `tbl_boxes`.`transcription` AS `transcription`,
                `tbl_languages`.`language` AS `language`
            FROM `tbl_pages`
                INNER JOIN `tbl_boxes` ON `tbl_boxes`.`page_id` = `tbl_pages`.`id`
                INNER JOIN `tbl_languages` ON `tbl_boxes`.`language_id` = `tbl_languages`.`id`
            WHERE
                `tbl_pages`.`page_fname` = :page_fname
            ORDER BY
                `box_x` ASC, `box_y` ASC
            ;
        ');
        $stmt->bindValue(':page_fname', $pageFName);
        $stmt->execute();

        $dataRows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        for ($i = 0; $i < count($dataRows); $i++) {
            $dataRows[$i]['box_x'] = intval($dataRows[$i]['box_x']);
            $dataRows[$i]['box_y'] = intval($dataRows[$i]['box_y']);
        }

        $response = $dataRows;
    }
    
    /*******************************/
    elseif ($submit == 'update') {
        if (!array_key_exists('page_fname', $_REQUEST)) {
            throw new Exception('Missing page_fname in request.');
        }
        $pageFName = $_REQUEST['page_fname'];
        if (mb_strlen($pageFName) != 12) {
            throw new Exception('page_fname is not the right length.');
        }
        
        if (!array_key_exists('box_x', $_REQUEST)) {
            throw new Exception('Missing box_x in request.');
        }
        $boxX = $_REQUEST['box_x'];
        if (!is_numeric($boxX) || $boxX < 0) {
            throw new Exception('box_x is not numeric.');
        }
        
        if (!array_key_exists('box_y', $_REQUEST)) {
            throw new Exception('Missing box_y in request.');
        }
        $boxY = $_REQUEST['box_y'];
        if (!is_numeric($boxY) || $boxY < 0) {
            throw new Exception('box_y is not numeric.');
        }
        
        if (!array_key_exists('transcription', $_REQUEST)) {
            throw new Exception('Missing transcription in request.');
        }
        $transcription = $_REQUEST['transcription'];
        
        if (!array_key_exists('language', $_REQUEST)) {
            throw new Exception('Missing language in request.');
        }
        $language = $_REQUEST['language'];
        
        try {
            $db->beginTransaction();

            $stmt = $db->prepare('
                UPDATE
                    `tbl_pages`
                    INNER JOIN `tbl_boxes` ON `tbl_boxes`.`page_id` = `tbl_pages`.`id`
                SET
                    `tbl_boxes`.`transcription` = :transcription,
                    `tbl_boxes`.`language_id` = (
                        SELECT `tbl_languages`.`id` FROM `tbl_languages` WHERE `tbl_languages`.`language` = :language
                    )
                WHERE
                    `tbl_pages`.`page_fname` = :page_fname
                    AND `tbl_boxes`.`x` = :box_x
                    AND `tbl_boxes`.`y` = :box_y
                ;
            ');
            $stmt->bindValue(':page_fname', $pageFName);
            $stmt->bindValue(':box_x', $boxX);
            $stmt->bindValue(':box_y', $boxY);
            $stmt->bindValue(':transcription', $transcription);
            $stmt->bindValue(':language', $language);
            if (!$stmt->execute()) {
                throw new Exception('Boxes table could not be updated.');
            }

            $db->commit();

            $response = array(
                'status' => 'success'
            );
        } catch (Exception $e) {
            $db->rollBack();

            throw $e;
        }
    }
    
    /*******************************/
    else {
        throw new Exception('Unknown submit value "' . $submit . '".');
    }

    $output = array(
        'errorMessage' => null,
        'response' => $response,
    );
}
catch (Exception $e) {
    $output = array(
        'errorMessage' => $e->getMessage(),
        'response' => null
    );
}

header('Content-Type: application/json');
echo json_encode($output);
?>