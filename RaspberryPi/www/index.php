<?php

$ini_array = parse_ini_file("photobooth.ini");

function createLockFile($lockFile) {
   $handle = fopen($lockFile, "w") or die("Unable to open file!");
   fclose($handle);
}

function deleteLockFile($lockFile) {
   unlink($lockFile);
}

function checkLockFile($lockFile) {
   if (file_exists($lockFile)) {
      return true;
   } else {
      return false;
   }
}

function takePhoto($galleryPath) {
   $date = new DateTime();
   $name = $date->format('Ymd-His') . ".jpg";
   $completeName = $galleryPath . $date->format('Ymd-His') . ".jpg";

   $output = shell_exec("raspistill -t 1 -o $completeName 2>&1");
   if ($output) {
      echo "<pre>$output</pre>";
   }
   return $name;
}

function createThumb($galleryPath, $thumbPath, $imageName) {
   $image = imagecreatefromjpeg($galleryPath.$imageName);
   $width = imagesx($image);
   $height = imagesy($image);
   $widthNew = 160;
   $heightNew = floor($height * ($widthNew / $width));
   $imageTemp = imagecreatetruecolor( $widthNew, $heightNew );
   imagecopyresized($imageTemp, $image, 0, 0, 0, 0, $widthNew, $heightNew, $width, $height);
   imagejpeg($imageTemp, $thumbPath.$imageName);
}

if (!checkLockFile($ini_array['LOCK_FILE'])) {
   createLockFile($ini_array['LOCK_FILE']);
   $name = takePhoto($ini_array['GALLERY_PATH']);
   createThumb($ini_array['GALLERY_PATH'], $ini_array['THUMB_PATH'], $name);
   deleteLockFile($ini_array['LOCK_FILE']);
   header ("refresh: 0; url=index.php");
}

?>

