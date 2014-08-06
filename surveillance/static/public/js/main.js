/* --------------------------------------------------------------------------
 *  JQuery Ready
 * --------------------------------------------------------------------------*/
$(document).ready( function()
    {
        $(window).scroll( lazyLoadImages );
        $(window).resize(function () {
            // This order needs to be maintained to avoid problems with the
            // large image view area sizing and particularly with leaving image
            // placeholders unloaded on a big resize like window maximizing.
            windowResize();
            largeImageViewAreaResize();
            lazyLoadImages();
        });

        $( '#large-image-view-area').resizable( { handles: 'e, w', stop: largeImageViewAreaResize } );

        // Immediately trigger a window resize to get initial sizing
        windowResize();
    }
);

function windowResize()
{
    // Update the large-image-view-area height to account for the new window size
    var headerHeight = $( '#header-area' ).height();
    var windowHeight = $( window ).height();

    $( '#large-image-view-area' ).css( 'height', windowHeight - headerHeight );
}

function largeImageViewAreaResize( event, ui )
{
    // Update the large-image max-width and max-height based on its view area
    var largeImageViewAreaWidth = $( '#large-image-view-area' ).width();
    var largeImageViewAreaHeight = $( '#large-image-view-area' ).height();

    $( '#large-image').css( 'max-height', largeImageViewAreaHeight );
    $( '#large-image').css( 'max-width', largeImageViewAreaWidth );

    // Update the navigation-area width based on the new large-image-view-area width
    var windowWidth = $( window ).width();

    $( '#navigation-area' ).css( 'width', windowWidth - largeImageViewAreaWidth );
}

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
    // No images!
    if( $( 'ul.hoverbox > li' ).size() <= 0 ) {
        return;
    }

    // Iterate through the images, checking if any images visible in the viewport
    // (even just a sliver) are not yet loaded. These blank placeholders in the
    // viewport get their <img src=""> updated so the images will load.
    for( var i = 0; i < $( 'ul.hoverbox > li' ).size(); i++ ) {
        var li = $( 'ul.hoverbox > li:nth-child(' + (i+1) + ')' );

        if( li.is( '[blank]' ) && isElementInViewport( li ) ) {
            var src = li.attr( 'blank' );
            li.removeAttr( 'blank' );
            li.html( '<a href="#"><img src="' + src + '" alt="description" />' +
                '<img src="' + src + '" alt="description" class="preview" /></a>' );
        }
    }
}

/* --------------------------------------------------------------------------
 *  Update Helper
 * --------------------------------------------------------------------------*/
function updateWithImages( json )
{
    // Loop over the images list and append a blank image placeholder for each
    // to the hoverbox ul. Each li contains a "blank" attr set to the src URL
    // to push to the img tags when we want to load the images.
    for( var i = 0; i < json.imgurls.length; i++ ) {
        $( 'ul.hoverbox').append( '<li blank="' + json.imgurls[i] + '"><a href="#"><img src="" />' +
            '<img src="" alt="description" class="preview" /></a></li>' );
    }

    // Initialize the large image viewer area
    $( '#large-image' ).attr( 'src', json.imgurls[0] + '&size=f' );
    largeImageViewAreaResize( null, null );

    // Do an initial call to the lazy image loading handler so any images
    // initially in the viewport are filled.
    lazyLoadImages();
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