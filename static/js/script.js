$(function(){
    $('.section-title').live('click', function()
    {
        $(this).parent().find('.section-content').slideToggle('slow');
    });
    
    $('.startup-closed > .section-content').hide();
});
