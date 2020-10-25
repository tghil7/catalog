/**
 * Created by Anicet on 10/18/2015.
 * Just modified the filename to see if that resolves the display issue. 
 */
 
 $('.elem').on('click', function () {
  $('#home').removeClass('active');
   $(this).addClass('active');
});
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



