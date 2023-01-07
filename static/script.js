$(document).ready(function(){

    $('.info').on('click', function(ev){
        var $this = $(this);
        var ile_jest_textarea = $this.children('.info_content').children('textarea').length;
        var run = true;
        if (ile_jest_textarea > 0) {
            if ($(ev.target).is('textarea')){
                run = false;
            }
        }
        if (run == true) {
            var hash = $this.parent().parent().attr('hash')
            var result = $.ajax({
                type : 'POST',
                url : '/process_get_info',
                data : {'hash': hash}
            })
            result.done(function(response){
                if (ile_jest_textarea == 0) {
                    $this.children('.info_content').html('<textarea class="info_content_text">' + response + '</textarea>')
                } else {
                    if (response.length > 0){
                        $this.children('.info_content').html(response)
                    } else {
                        $this.children('.info_content').html('Click to add info')
                    }
                }
            })
            result.fail(function(response){
                $this.children('.info_content').html('Error loaded data...')
            })
        }
    });

    $('.info').on('keyup', '.info_content_text', function(){
        var $this = $(this);
        var textvalue = $this.val()
        hash = $this.parent().parent().parent().parent().attr('hash')
        var result = $.ajax({
            type : 'POST',
            url : '/process_set_info',
            data : {'text': textvalue, 'hash': hash}
        });
        result.done(function(response){
            $this.children('.info_content').html(response)
        });
        result.fail(function(response){
            $this.children('.info_content').html('Error saved data...')
        });


    })

});