<?php

$ini_array = parse_ini_file("photobooth.ini");

function getFile($folder) {
   chdir($folder);
   $dir = '';

   $arraylistafiles = glob($dir.'*.jpg');

   return end($arraylistafiles);
}

function showStartPage($folderThumb, $folderImage, $thumbRelativePath, $relativePath) {
echo <<< EOT
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>photobooth</title>
</head>
<body>
<a href="gallery">gallery</a>
<br>
<a href="
EOT;

echo $relativePath.getFile($folderThumb);

echo <<< EOT
">
<img src="
EOT;

echo $thumbRelativePath.getFile($folderThumb);

echo <<< EOT
" title="
EOT;

echo getFile($folderImage);

echo <<< EOT
" width="256">
</a>
<form method="post" action="takePhoto.php">
<input type="submit" value="take a photo">
</form>
</body>
</html>
EOT;
}

showStartPage($ini_array['THUMB_PATH'], $ini_array['GALLERY_PATH'], $ini_array['RELATIVE_THUMB_PAT
H'], $ini_array['RELATIVE_PATH']);

?>

