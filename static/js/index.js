$(function(){
  
  $('#images').change(function(e) {
    var files = e.target.files;
    for (var i = 0; i <= files.length; i++) {
      
      // when i == files.length reorder and break
      if(i==files.length){
        // need timeout to reorder beacuse prepend is not done
        setTimeout(function(){ reorderImages(); }, 100);
        break;
      }
      
      var file = files[i];
      var reader = new FileReader();
      
      reader.onload = (function(file) {
        return function(event){
          $('#sortable').prepend('<li class="ui-state-default" data-order=0 data-id="'+file.lastModified+'"><img src="' + event.target.result + '" style="width:100%;" /> <div class="order-number">0</div></li>');
        };
      })(file);
      
      reader.readAsDataURL(file);
    }// end for;
    
  });
  
  $('#sortable').sortable();
  $('#sortable').disableSelection();
  
  //sortable events
  $('#sortable').on('sortbeforestop',function(event){
    
    reorderImages();
    
  });
  
  
  function reorderImages(){
    // get the items
    var images = $('#sortable li');
    
    var i=0, nrOrder=0;
    for(i;i<images.length;i++){
      
      var image = $(images[i]);
      
      if( image.hasClass('ui-state-default') && !image.hasClass('ui-sortable-placeholder') ){
        image.attr('data-order', nrOrder);
        var orderNumberBox = image.find('.order-number');
        orderNumberBox.html(nrOrder+1);
        nrOrder++;
      }// end if;
      
    }// end for;
  }
  
 });