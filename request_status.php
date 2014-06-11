<?php
function deliverResult($requestid, $error, $orig_url, $status, $title, $type, $extract_url, $src_url, $dest_url)
{
    $result = array();
    $result['requestid'] = $requestid;
    $result['status'] = $status;
    $result['orginalURL'] = $orig_url;
    if(is_null($error))
    {
        if(!is_null($type))
        {
            $result['type'] = $type;
            $result['title'] = $title;
            $result['extractURL'] = $extract_url;
        }
        if(!is_null($src_url))
        {
            $result['sourceURL'] = $src_url;
        }
        if(!is_null($dest_url))
        {
            $result['destURL'] = $dest_url;
        }
    }
    else
    {
        $result['error'] = $error;
    }    
    echo json_encode($result);
    exit;
}

$userid = null;
$requestid = null;
$error = null;
$orig_url = null;
$status = null;
$title = null;
$type = null;
$extract_url = null;
$src_url = null;
$dest_url = null;

if(!isset($_POST['userid']) || !isset($_POST['requestid']))
{
    $error = 'Bad request';
    error_log("Missing request parameters");
    deliverResult($requestid, $error, $orig_url, $status,$title, $type, $extract_url, $src_url, $dest_url);
}
$userid = $_POST['userid'];
$requestid = $_POST['requestid'];

$sql_host = '167.88.34.62';
$sql_user = 'Brun0';
$sql_password = '65UB3b3$';
$sql_table = 'vidblit';

$con = mysqli_connect($sql_host,$sql_user,$sql_password,$sql_table);
if (mysqli_connect_errno())
{
    $error = 'Technical difficulties';
    error_log("Failed to connect to MySQL " . mysqli_connect_error());
    deliverResult($requestid, $error, $orig_url, $status,$title, $type, $extract_url, $src_url, $dest_url);
}

$sql_userid = $con->real_escape_string($_POST['userid']);
$sql_requestid = $con->real_escape_string($_POST['requestid']);
$sql = 'select r.requestid as rid, ' .
        ' r.url as orig_url, ' .
        ' r.status as status, ' .
        ' r.error as error,  ' .
        ' e.title as title, ' .
        ' e.type as type, ' .
        ' e.url as extract_url, ' .
        ' l.src_url as src_url, ' .
        ' l.dest_url as dest_url ' .
        ' from requests r ' .
        ' left join request_locations l on r.requestid=l.requestid ' .
        ' left join request_extractresults e on r.requestid=e.requestid' .
        ' where r.requestid=' . $sql_requestid .
        ' and r.userid=' . $sql_userid;

$result = $con->query($sql);
if(!$result)
{
    $error = 'Technical difficulties';
    error_log("Error creating request in MySQL " . mysqli_error());
    deliverResult($requestid, $error, $orig_url, $status,$title, $type, $extract_url, $src_url, $dest_url);
}

$value = $result->fetch_object();
$orig_url = $value->orig_url;
$status = $value->status;
$error = $value->error;
$title = $value->title;
$type = $value->type;
$extract_url = $value->extract_url;
$src_url = $value->src_url;
$dest_url = $value->dest_url;

mysqli_close($con);
deliverResult($requestid, $error, $orig_url, $status,$title, $type, $extract_url, $src_url, $dest_url);
?>
