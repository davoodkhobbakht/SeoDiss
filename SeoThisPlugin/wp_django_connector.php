<?php
/**
 * Plugin Name: SeoThis Connector
 * Description: Connects WooCommerce to a Django API to use SeoThis services.
 * Version: 1.0
 * Author: Your Name
 */

if (!defined('ABSPATH')) {
    exit;
}

define('WPDC_PLUGIN_DIR', plugin_dir_path(__FILE__));

require_once WPDC_PLUGIN_DIR . 'admin/admin-page.php';
require_once WPDC_PLUGIN_DIR . 'includes/ajax-handler.php';

function wpdc_enqueue_admin_scripts($hook) {
    if (strpos($hook, 'product') !== false) {
        wp_enqueue_script('wpdc-admin-js', plugin_dir_url(__FILE__) . 'assets/js/admin.js', ['jquery'], '1.0', true);
        wp_localize_script('wpdc-admin-js', 'wpdc_ajax_obj', [
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('wpdc_nonce')
        ]);
    }
}
add_action('admin_enqueue_scripts', 'wpdc_enqueue_admin_scripts');
