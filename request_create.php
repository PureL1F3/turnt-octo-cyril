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

$requestid = null;;
$error = null;

if(!isset($_POST['userid']) || !isset($_POST['url']))
{
    $error = 'Bad request';
    error_log("Missing request parameters");
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
    error_log("Failed to connect to MySQL " . mysqli_connect_error());
    deliverResult($requestid, $error);
}

$sql_userid = $con->real_escape_string($_POST['userid']);
$sql_url = $con->real_escape_string($_POST['url']);
$sql = "CALL request_create('$sql_userid', '$sql_url');";

apache_note('Executing the following mysql:\n'.$sql);
$result = $con->query($sql);
if(!$result)
{
    $error = 'Technical difficulties';
    error_log("Error creating request in MySQL " . mysqli_error());
    deliverResult($requestid, $error);
}

$value = $result->fetch_object();
$requestid = $value->requestid;
mysqli_close($con);

deliverResult($requestid, $error);

?>
