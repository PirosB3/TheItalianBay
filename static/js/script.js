$(function(){
    
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
    
    // Create custom urls on form
    $('#search-form').submit(function(e)
    {
        e.preventDefault();
        
        // if field is empty, just return
        if (document.getElementById('search-field').value.length == 0) { return; }
        
        // start forming custom url
        var value = document.getElementById('search-field').value
        var filter = getFilter();
        
        // replace url with the constructed one
        document.location = "http://theitalianbay.appspot.com/s/" + value + "/" + filter;
    });
    
    // Helper function, returns the first checked filter in the search form
    function getFilter()
    {
        filter = "";
        
        $('#filter-field > input[type=checkbox]').each(function(k,v)
        {
            if(v.checked)
            {
                filter = ("f/" + v.value + "/");
            }
        });
        return filter;
    }
});
