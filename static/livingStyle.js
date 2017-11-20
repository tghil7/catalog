/**
 * Created by Anicet on 10/18/2015.
 */
function playImage()
{
  if (document.getElementById("image_link").innerText === "View larger image")
  {
    $("#thumb_cottage").attr("src", "cottage_large.jpg");
    document.getElementById("image_link").innerText ="View smaller image";
  }
  else if (document.getElementById("image_link").innerText === "View smaller image")
  {
    $("#thumb_cottage").attr("src", "cottage_small.jpg");
    document.getElementById("image_link").innerText ="View larger image";
  }
}



