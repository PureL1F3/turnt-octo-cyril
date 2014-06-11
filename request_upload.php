<?php

function deliverResult($requestid, $error)
{
    $result = array();
    if(is_null($error))
    {
        $result['success'] = true;
        $result['requestid'] = $requestid;
    }
    else
    {
        $result['success'] = false;
        $result['error'] = $error;
    }
    
    echo json_encode($result);
    exit;
}

$error = null;
$requestid = null;

if(!(isset($_POST['requestid']) && isset($_POST['userid']) && isset($_POST['length'])) || empty($_FILES))
{
    $error = 'Bad request';
    error_log("Either some details are ommitted or file is missing", 0);
    deliverResult($requestid, $error);
}

$file = $_FILES['file']['tmp_name'];
if(empty($file) || !is_uploaded_file($file))
{
    $error = 'Bad request';
    error_log("Either file is empty or not an uploaded file", 0);
    deliverResult($requestid, $error);
}
$cname=str_replace(" ","_",$file);

$requestid = $_POST['requestid'];
$userid = $_POST['userid'];
$length = $_POST['length'];

$target_path = '/vidblit/uploads/' . $requestid;
if(!move_uploaded_file($file, $target_path))
{
    $error = 'Technical difficulties';
    error_log("Failed to copy uploaded file to path $target_path", 0);
    deliverResult($requestid, $error);
}

$sql_host = '167.88.34.62';
$sql_user = 'Brun0';
$sql_password = '65UB3b3$';
$sql_table = 'vidblit';
$con = mysqli_connect($sql_host,$sql_user,$sql_password,$sql_table);
if (mysqli_connect_errno())
{
    $error = 'Technical difficulties';
    error_log("Failed to connect to MySQL " . mysqli_connect_error(), 0);
    deliverResult($requestid, $error);
}
$sql = "CALL request_create_upload($requestid, '$target_path', $length);";
$con->query($sql);
mysqli_close($con);

deliverResult($requestid, $error);

?>
