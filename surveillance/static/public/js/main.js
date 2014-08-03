/* --------------------------------------------------------------------------
 *  JQuery Ready
 * --------------------------------------------------------------------------*/
$(document).ready( function()
    {
        $(window).scroll( lazyLoadImages );
        $(window).resize( lazyLoadImages );
    }
);

/* --------------------------------------------------------------------------
 *  Submit Handler
 * --------------------------------------------------------------------------*/
function submitClick()
{
    var start = document.getElementById("start");
    var end = document.getElementById("end");

    // Form the URL with start & end queries for the available-images call
    var url = '/availableimages?start=' + start.value + '&end=' + end.value;

    // Get the images list using an asynchronous call
    var json = $.ajax(
        {
            url: url,
            dataType: 'jsonp',
            success: updateWithImages
        });
}
/* --------------------------------------------------------------------------
 *  Lazy Image Loading
 * --------------------------------------------------------------------------*/
function lazyLoadImages()
{
    if( $( 'ul.hoverbox > li' ).size() <= 0 ) {
        return;
    }

    var data = $( 'ul.hoverbox' ).data();

    for( var i = 0; i < $( 'ul.hoverbox > li' ).size(); i++ ) {
        var li = $( 'ul.hoverbox > li:nth-child(' + (i+1) + ')' );

        if( li.is( '[blank]' ) && isElementInViewport( li ) ) {
            li.removeAttr( 'blank' );
            li.html( '<a href="#"><img src="' + data.imgurls[i] + '" alt="description" /><img src="' + data.imgurls[i] + '" alt="description" class="preview" /></a>' );
        }
    }
}

/* --------------------------------------------------------------------------
 *  Viewport Helper
 * --------------------------------------------------------------------------*/
function isElementInViewport( el ) {

    //special bonus for those using jQuery
    if (el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        (
            (rect.left >= 0 && rect.right <= $(window).width() ) ||               // Inside
            (rect.left < 0 && rect.right >= 0 ) ||                                // Cross left boundary
            (rect.left <= $(window).width() && rect.right > $(window).width())    // Cross right boundary
        ) &&
        (
            (rect.top >= 0 && rect.bottom <= $(window).height() ) ||              // Inside
            (rect.top < 0 && rect.bottom >= 0 ) ||                                // Cross top boundary
            (rect.top <= $(window).height() && rect.bottom > $(window).height())  // Cross bottom boundary
         )
    );
}

/* --------------------------------------------------------------------------
 *  Update Helper
 * --------------------------------------------------------------------------*/
function updateWithImages( json )
{
    // Loop over the images list and append a placeholder for each to
    // the hoverbox ul. These will be dynamically filled as they are
    // shown in the viewport.
    for( var i = 0; i < json.imgurls.length; i++ ) {
        $( 'ul.hoverbox').append( '<li blank="blank"><a href="#"><img src="" /><img src="" alt="description" class="preview" /></a></li>' );
    }

    // Setup data on the images list to dynamically load images.
    $( 'ul.hoverbox' ).data( 'imgurls', json.imgurls );

    // Do an initial call to the scroll handler so the images in the
    // viewport right now are filled in.
    lazyLoadImages();
}