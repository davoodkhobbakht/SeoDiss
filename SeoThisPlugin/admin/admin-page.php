<?php
function wpdc_add_admin_menu() {
    add_menu_page(
        'WP Django Connector',
        'Django Connector',
        'manage_options',
        'wpdc-settings',
        'wpdc_settings_page'
    );
}
add_action('admin_menu', 'wpdc_add_admin_menu');

function wpdc_settings_page() {
    ?>
    <div class="wrap">
        <h1>WooCommerce Credentials</h1>
        <form method="post" action="options.php">
            <?php
            settings_fields('wpdc_settings_group');
            do_settings_sections('wpdc-settings');
            submit_button();
            ?>
        </form>
    </div>
    <?php
}

function wpdc_register_settings() {
    register_setting('wpdc_settings_group', 'wpdc_consumer_key');
    register_setting('wpdc_settings_group', 'wpdc_consumer_secret');

    add_settings_section('wpdc_settings_section', 'API Credentials', null, 'wpdc-settings');

    add_settings_field(
        'wpdc_consumer_key',
        'Consumer Key',
        'wpdc_consumer_key_callback',
        'wpdc-settings',
        'wpdc_settings_section'
    );

    add_settings_field(
        'wpdc_consumer_secret',
        'Consumer Secret',
        'wpdc_consumer_secret_callback',
        'wpdc-settings',
        'wpdc_settings_section'
    );
}
add_action('admin_init', 'wpdc_register_settings');

function wpdc_consumer_key_callback() {
    $value = get_option('wpdc_consumer_key');
    echo "<input type='text' name='wpdc_consumer_key' value='" . esc_attr($value) . "' class='regular-text' />";
}

function wpdc_consumer_secret_callback() {
    $value = get_option('wpdc_consumer_secret');
    echo "<input type='text' name='wpdc_consumer_secret' value='" . esc_attr($value) . "' class='regular-text' />";
}
