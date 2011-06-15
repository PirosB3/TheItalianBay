$(function(){
    
    // Validate Search Field
    $('#search-form').submit(function(e)
    {
        if ($('search-field').text().length == 0)
        {
            e.preventDefault();
        }
    })
    
    // For Sections
    $('.section-title').live('click', function()
    {
        $(this).parent().find('.section-content').slideToggle('slow');
    });
    
    $('.startup-closed > .section-content').hide();
    
    // For Table
    $('#results tr').hover(
        function()
        {
            $(this).addClass('hover');
        },
        function()
        {
            $(this).removeClass('hover');
        }
    );
});
