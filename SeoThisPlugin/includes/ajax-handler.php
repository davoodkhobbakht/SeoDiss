<?php
add_action('admin_footer', 'wpdc_add_generate_button');
function wpdc_add_generate_button() {
    global $pagenow, $post;

    if ($pagenow === 'post.php' && get_post_type($post) === 'product') {
        echo '<button id="wpdc-generate-btn" class="button button-primary">Generate Article via Django</button>';
    }
}

add_action('wp_ajax_wpdc_send_to_django', 'wpdc_send_to_django_callback');
function wpdc_send_to_django_callback() {
    check_ajax_referer('wpdc_nonce', 'nonce');

    $product_id = intval($_POST['product_id']);
    $consumer_key = get_option('wpdc_consumer_key');
    $consumer_secret = get_option('wpdc_consumer_secret');

    $response = wp_remote_post('https://dioti.ir/api/update-product/', [
        'method' => 'POST',
        'headers' => [
            'Content-Type' => 'application/json',
        ],
        'body' => json_encode([
            'product_id' => $product_id,
            'consumer_key' => $consumer_key,
            'consumer_secret' => $consumer_secret,
        ])
    ]);

    wp_send_json(wp_remote_retrieve_body($response));
}
