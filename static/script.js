$(document).ready(function(){
  $('.product').on('click', function(){
    $this = $(this)
    console.log('jestem')

    $.ajax({
      type: "POST",
      url: "/save-art-for-user",
      success: function(response) {
        console.log(response);
      }
    });
    

  });
});