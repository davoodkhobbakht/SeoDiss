jQuery(document).ready(function($) {
    $('#wpdc-generate-btn').on('click', function(e) {
        e.preventDefault();
        const productId = window.location.href.match(/post=([0-9]+)/)[1];

        $.post(wpdc_ajax_obj.ajax_url, {
            action: 'wpdc_send_to_django',
            nonce: wpdc_ajax_obj.nonce,
            product_id: productId
        }, function(response) {
            alert('Django API response: ' + response);
        });
    });
});
