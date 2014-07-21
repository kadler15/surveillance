$(document).ready( function()
    {
		// Attach a click handler to submit through jQuery
        $('#submit').click(function() {
            var start = document.getElementById("start");
            var end = document.getElementById("end");

			// Form the URL with start & end queries for the available-images call
            var url = '/available-images.json?start=' + start.value + '&end=' + end.value;
			
			// Get the images list using an asynchronous call
            var json = $.ajax(
                {
                    url: url,
                    dataType: 'jsonp',
                    success: function( json ) {
						// Loop over the images list and replace the contents of the
						// internal contents of the images div with the images.
                        var inner = '';
                        for( var i = 0; i < json.imgurls.length; i++ )
                        {
                            inner += '<img src="' + json.imgurls[i] + '"><br>';
                        }
                        document.getElementById('images').innerHTML = inner;
                    }
                });
        });
    }
);