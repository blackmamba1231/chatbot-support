# Vogo.Family WooCommerce API Documentation
Generated at: 2025-04-19T15:05:36.474844

## Base URL
https://vogo.family/wp-json/

## Authentication
- Type: Basic Auth
- Parameters:
  - consumer_key: WP_CONSUMER_KEY environment variable
  - consumer_secret: WP_CONSUMER_SECRET environment variable

## Endpoints

### Products

#### List Products
- Method: GET
- Endpoint: `products`
- Response Structure:
```json
{
  "id": 32671,
  "name": "Vaslui - Proxima Shopping Center",
  "slug": "vaslui-proxima-shopping-center",
  "permalink": "https://vogo.family/product/vaslui-proxima-shopping-center/",
  "date_created": "2025-04-09T22:56:36",
  "date_created_gmt": "2025-04-09T20:56:36",
  "date_modified": "2025-04-10T20:40:08",
  "date_modified_gmt": "2025-04-10T18:40:08",
  "type": "simple",
  "status": "publish",
  "featured": false,
  "catalog_visibility": "visible",
  "description": "<p>Livrare produse din Proxima Shopping Center - Vaslui - pret de baza; pretul poate varia in functie de numarul de produse, magazin si distanta)</p>\n",
  "short_description": "<p>Vaslui &#8211; Proxima Shopping Center</p>\n",
  "sku": "617ae7e16bc3",
  "price": "99",
  "regular_price": "99",
  "sale_price": "",
  "date_on_sale_from": null,
  "date_on_sale_from_gmt": null,
  "date_on_sale_to": null,
  "date_on_sale_to_gmt": null,
  "on_sale": false,
  "purchasable": true,
  "total_sales": 8,
  "virtual": false,
  "downloadable": false,
  "downloads": [],
  "download_limit": -1,
  "download_expiry": -1,
  "external_url": "",
  "button_text": "",
  "tax_status": "none",
  "tax_class": "",
  "manage_stock": false,
  "stock_quantity": null,
  "backorders": "no",
  "backorders_allowed": false,
  "backordered": false,
  "low_stock_amount": null,
  "sold_individually": false,
  "weight": "",
  "dimensions": {
    "length": "",
    "width": "",
    "height": ""
  },
  "shipping_required": true,
  "shipping_taxable": false,
  "shipping_class": "",
  "shipping_class_id": 0,
  "reviews_allowed": false,
  "average_rating": "0.00",
  "rating_count": 0,
  "upsell_ids": [],
  "cross_sell_ids": [],
  "parent_id": 0,
  "purchase_note": "",
  "categories": [
    {
      "id": 223,
      "name": "Mall Delivery",
      "slug": "mall-delivery"
    }
  ],
  "tags": [],
  "images": [
    {
      "id": 32762,
      "date_created": "2025-04-10T22:39:05",
      "date_created_gmt": "2025-04-10T18:39:05",
      "date_modified": "2025-04-10T22:39:31",
      "date_modified_gmt": "2025-04-10T18:39:31",
      "src": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1",
      "name": "Alba Iulia Carolina Mall",
      "alt": ""
    }
  ],
  "attributes": [],
  "default_attributes": [],
  "variations": [],
  "grouped_products": [],
  "menu_order": 0,
  "price_html": "<span class=\"woocommerce-Price-amount amount\"><bdi>99,00&nbsp;<span class=\"woocommerce-Price-currencySymbol\">lei</span></bdi></span>",
  "related_ids": [
    32507,
    32473,
    32503,
    32499,
    32491
  ],
  "meta_data": [
    {
      "id": 311901,
      "key": "_wp_page_template",
      "value": "default"
    },
    {
      "id": 315928,
      "key": "woodmart_sguide_select",
      "value": "none"
    },
    {
      "id": 315929,
      "key": "jk_sku",
      "value": ""
    },
    {
      "id": 315930,
      "key": "custom_package_number",
      "value": ""
    },
    {
      "id": 315931,
      "key": "custom_product_type",
      "value": ""
    },
    {
      "id": 315932,
      "key": "_is_subscription",
      "value": "no"
    },
    {
      "id": 315933,
      "key": "acquired_price",
      "value": ""
    },
    {
      "id": 315934,
      "key": "woodmart_price_unit_of_measure",
      "value": ""
    },
    {
      "id": 315935,
      "key": "woodmart_fbt_bundles_id",
      "value": [
        ""
      ]
    },
    {
      "id": 315936,
      "key": "woodmart_total_stock_quantity",
      "value": ""
    },
    {
      "id": 315937,
      "key": "woodmart_wc_video_gallery",
      "value": {
        "32762": {
          "video_type": "mp4",
          "upload_video_id": "",
          "upload_video_url": "",
          "youtube_url": "",
          "vimeo_url": "",
          "autoplay": "0",
          "video_size": "contain",
          "video_control": "theme",
          "hide_gallery_img": "0",
          "hide_information": "0",
          "audio_status": "unmute"
        }
      }
    },
    {
      "id": 315938,
      "key": "_product_360_image_gallery",
      "value": ""
    },
    {
      "id": 315939,
      "key": "want_translated",
      "value": [
        "yes"
      ]
    },
    {
      "id": 315940,
      "key": "_want_translated",
      "value": "field_67b6c194131d0"
    },
    {
      "id": 315941,
      "key": "_woodmart_whb_header",
      "value": "none"
    },
    {
      "id": 315942,
      "key": "_woodmart_main_layout",
      "value": "default"
    },
    {
      "id": 315943,
      "key": "_woodmart_sidebar_width",
      "value": "default"
    },
    {
      "id": 315944,
      "key": "_woodmart_custom_sidebar",
      "value": "none"
    },
    {
      "id": 315945,
      "key": "_woodmart_new_label",
      "value": ""
    },
    {
      "id": 315946,
      "key": "_woodmart_new_label_date",
      "value": ""
    },
    {
      "id": 315947,
      "key": "_woodmart_swatches_attribute",
      "value": ""
    },
    {
      "id": 315948,
      "key": "_woodmart_related_off",
      "value": ""
    },
    {
      "id": 315949,
      "key": "_woodmart_exclude_show_single_variation",
      "value": ""
    },
    {
      "id": 315950,
      "key": "_woodmart_product_video",
      "value": ""
    },
    {
      "id": 315951,
      "key": "_woodmart_product_hashtag",
      "value": ""
    },
    {
      "id": 315952,
      "key": "_woodmart_single_product_style",
      "value": "inherit"
    },
    {
      "id": 315953,
      "key": "_woodmart_thums_position",
      "value": "inherit"
    },
    {
      "id": 315954,
      "key": "_woodmart_extra_content",
      "value": ""
    },
    {
      "id": 315955,
      "key": "_woodmart_extra_position",
      "value": "after"
    },
    {
      "id": 315956,
      "key": "_woodmart_product_design",
      "value": "inherit"
    },
    {
      "id": 315957,
      "key": "_woodmart_product-background",
      "value": ""
    },
    {
      "id": 315958,
      "key": "_woodmart_hide_tabs_titles",
      "value": ""
    },
    {
      "id": 315959,
      "key": "_woodmart_product_custom_tab_title",
      "value": ""
    },
    {
      "id": 315960,
      "key": "_woodmart_product_custom_tab_content_type",
      "value": "text"
    },
    {
      "id": 315961,
      "key": "_woodmart_product_custom_tab_content",
      "value": ""
    },
    {
      "id": 315962,
      "key": "_woodmart_product_custom_tab_html_block",
      "value": ""
    },
    {
      "id": 315963,
      "key": "_woodmart_product_custom_tab_title_2",
      "value": ""
    },
    {
      "id": 315964,
      "key": "_woodmart_product_custom_tab_content_type_2",
      "value": "text"
    },
    {
      "id": 315965,
      "key": "_woodmart_product_custom_tab_content_2",
      "value": ""
    },
    {
      "id": 315966,
      "key": "_woodmart_product_custom_tab_html_block_2",
      "value": ""
    },
    {
      "id": 315967,
      "key": "_yoast_wpseo_primary_product_cat",
      "value": ""
    },
    {
      "id": 315968,
      "key": "_yoast_wpseo_primary_product_provider",
      "value": ""
    },
    {
      "id": 315969,
      "key": "_yoast_wpseo_content_score",
      "value": "90"
    },
    {
      "id": 315970,
      "key": "_yoast_wpseo_estimated-reading-time-minutes",
      "value": "1"
    },
    {
      "id": 326344,
      "key": "wd_page_css_files",
      "value": [
        "helpers-wpb-elem",
        "widget-recent-post-comments",
        "widget-nav",
        "widget-wd-layered-nav",
        "woo-mod-swatches-base",
        "woo-mod-swatches-filter",
        "widget-layered-nav-stock-status",
        "widget-slider-price-filter",
        "wpcf7",
        "revolution-slider",
        "woo-payments",
        "elementor-base",
        "elementor-pro-base",
        "woocommerce-base",
        "mod-star-rating",
        "woo-el-track-order",
        "woocommerce-block-notices",
        "woo-mod-quantity",
        "woo-opt-free-progress-bar",
        "woo-mod-progress-bar",
        "woo-single-prod-el-base",
        "woo-mod-stock-status",
        "woo-mod-shop-attributes",
        "wd-search-results",
        "wd-search-form",
        "mod-animations-keyframes",
        "animations",
        "woo-single-prod-builder",
        "woo-el-breadcrumbs-builder",
        "woo-single-prod-el-navigation",
        "woo-single-prod-el-gallery",
        "swiper",
        "swiper-arrows",
        "button",
        "accordion",
        "accordion-elem-wpb",
        "mod-comments",
        "tabs",
        "woo-single-prod-el-tabs-opt-layout-tabs",
        "product-loop",
        "product-loop-standard",
        "woo-mod-add-btn-replace",
        "woo-opt-stretch-cont",
        "woo-opt-title-limit",
        "swiper-pagin",
        "widget-collapse",
        "footer-base",
        "section-title",
        "mod-nav-menu-label",
        "scroll-top",
        "header-mod-content-calc",
        "widget-shopping-cart",
        "widget-product-list",
        "header-my-account-sidebar",
        "woo-mod-login-form",
        "cookies-popup",
        "bottom-toolbar",
        "mod-tools",
        "header-elements-base",
        "header-cart-side",
        "header-cart",
        "header-my-account"
      ]
    }
  ],
  "stock_status": "instock",
  "has_options": false,
  "post_password": "",
  "global_unique_id": "",
  "yoast_head": "<!-- This site is optimized with the Yoast SEO plugin v24.8.1 - https://yoast.com/wordpress/plugins/seo/ -->\n<title>Vaslui - Proxima Shopping Center - Vogo Family</title>\n<!-- Admin only notice: this page does not show a meta description because it does not have one, either write it for this page specifically or go into the [Yoast SEO - Settings] menu and set up a template. -->\n<meta name=\"robots\" content=\"index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1\" />\n<link rel=\"canonical\" href=\"https://vogo.family/product/vaslui-proxima-shopping-center/\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:locale\" content=\"en_US\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:type\" content=\"article\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:title\" content=\"Vaslui - Proxima Shopping Center - Vogo Family\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:description\" content=\"Vaslui - Proxima Shopping Center\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:url\" content=\"https://vogo.family/product/vaslui-proxima-shopping-center/\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:site_name\" content=\"Vogo Family\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"article:modified_time\" content=\"2025-04-10T18:40:08+00:00\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:image\" content=\"https://vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png\" class=\"yoast-seo-meta-tag\" />\n\t<meta property=\"og:image:width\" content=\"476\" class=\"yoast-seo-meta-tag\" />\n\t<meta property=\"og:image:height\" content=\"373\" class=\"yoast-seo-meta-tag\" />\n\t<meta property=\"og:image:type\" content=\"image/png\" class=\"yoast-seo-meta-tag\" />\n<meta name=\"twitter:card\" content=\"summary_large_image\" class=\"yoast-seo-meta-tag\" />\n<meta name=\"twitter:label1\" content=\"Est. reading time\" class=\"yoast-seo-meta-tag\" />\n\t<meta name=\"twitter:data1\" content=\"1 minute\" class=\"yoast-seo-meta-tag\" />\n<script type=\"application/ld+json\" class=\"yoast-schema-graph\">{\"@context\":\"https://schema.org\",\"@graph\":[{\"@type\":\"WebPage\",\"@id\":\"https://vogo.family/product/vaslui-proxima-shopping-center/\",\"url\":\"https://vogo.family/product/vaslui-proxima-shopping-center/\",\"name\":\"Vaslui - Proxima Shopping Center - Vogo Family\",\"isPartOf\":{\"@id\":\"https://vogo.family/#website\"},\"primaryImageOfPage\":{\"@id\":\"https://vogo.family/product/vaslui-proxima-shopping-center/#primaryimage\"},\"image\":{\"@id\":\"https://vogo.family/product/vaslui-proxima-shopping-center/#primaryimage\"},\"thumbnailUrl\":\"https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1\",\"datePublished\":\"2025-04-09T20:56:36+00:00\",\"dateModified\":\"2025-04-10T18:40:08+00:00\",\"breadcrumb\":{\"@id\":\"https://vogo.family/product/vaslui-proxima-shopping-center/#breadcrumb\"},\"inLanguage\":\"en-US\",\"potentialAction\":[{\"@type\":\"ReadAction\",\"target\":[\"https://vogo.family/product/vaslui-proxima-shopping-center/\"]}]},{\"@type\":\"ImageObject\",\"inLanguage\":\"en-US\",\"@id\":\"https://vogo.family/product/vaslui-proxima-shopping-center/#primaryimage\",\"url\":\"https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1\",\"contentUrl\":\"https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1\",\"width\":476,\"height\":373},{\"@type\":\"BreadcrumbList\",\"@id\":\"https://vogo.family/product/vaslui-proxima-shopping-center/#breadcrumb\",\"itemListElement\":[{\"@type\":\"ListItem\",\"position\":1,\"name\":\"Home\",\"item\":\"https://vogo.family/\"},{\"@type\":\"ListItem\",\"position\":2,\"name\":\"Magazin\",\"item\":\"https://vogo.family/shop/\"},{\"@type\":\"ListItem\",\"position\":3,\"name\":\"Vaslui &#8211; Proxima Shopping Center\"}]},{\"@type\":\"WebSite\",\"@id\":\"https://vogo.family/#website\",\"url\":\"https://vogo.family/\",\"name\":\"Vogo Family\",\"description\":\"\",\"potentialAction\":[{\"@type\":\"SearchAction\",\"target\":{\"@type\":\"EntryPoint\",\"urlTemplate\":\"https://vogo.family/?s={search_term_string}\"},\"query-input\":{\"@type\":\"PropertyValueSpecification\",\"valueRequired\":true,\"valueName\":\"search_term_string\"}}],\"inLanguage\":\"en-US\"}]}</script>\n<!-- / Yoast SEO plugin. -->",
  "yoast_head_json": {
    "title": "Vaslui - Proxima Shopping Center - Vogo Family",
    "robots": {
      "index": "index",
      "follow": "follow",
      "max-snippet": "max-snippet:-1",
      "max-image-preview": "max-image-preview:large",
      "max-video-preview": "max-video-preview:-1"
    },
    "canonical": "https://vogo.family/product/vaslui-proxima-shopping-center/",
    "og_locale": "en_US",
    "og_type": "article",
    "og_title": "Vaslui - Proxima Shopping Center - Vogo Family",
    "og_description": "Vaslui - Proxima Shopping Center",
    "og_url": "https://vogo.family/product/vaslui-proxima-shopping-center/",
    "og_site_name": "Vogo Family",
    "article_modified_time": "2025-04-10T18:40:08+00:00",
    "og_image": [
      {
        "width": 476,
        "height": 373,
        "url": "https://vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png",
        "type": "image/png"
      }
    ],
    "twitter_card": "summary_large_image",
    "twitter_misc": {
      "Est. reading time": "1 minute"
    },
    "schema": {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "WebPage",
          "@id": "https://vogo.family/product/vaslui-proxima-shopping-center/",
          "url": "https://vogo.family/product/vaslui-proxima-shopping-center/",
          "name": "Vaslui - Proxima Shopping Center - Vogo Family",
          "isPartOf": {
            "@id": "https://vogo.family/#website"
          },
          "primaryImageOfPage": {
            "@id": "https://vogo.family/product/vaslui-proxima-shopping-center/#primaryimage"
          },
          "image": {
            "@id": "https://vogo.family/product/vaslui-proxima-shopping-center/#primaryimage"
          },
          "thumbnailUrl": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1",
          "datePublished": "2025-04-09T20:56:36+00:00",
          "dateModified": "2025-04-10T18:40:08+00:00",
          "breadcrumb": {
            "@id": "https://vogo.family/product/vaslui-proxima-shopping-center/#breadcrumb"
          },
          "inLanguage": "en-US",
          "potentialAction": [
            {
              "@type": "ReadAction",
              "target": [
                "https://vogo.family/product/vaslui-proxima-shopping-center/"
              ]
            }
          ]
        },
        {
          "@type": "ImageObject",
          "inLanguage": "en-US",
          "@id": "https://vogo.family/product/vaslui-proxima-shopping-center/#primaryimage",
          "url": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1",
          "contentUrl": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Alba-Iulia-Carolina-Mall-1.png?fit=476%2C373&ssl=1",
          "width": 476,
          "height": 373
        },
        {
          "@type": "BreadcrumbList",
          "@id": "https://vogo.family/product/vaslui-proxima-shopping-center/#breadcrumb",
          "itemListElement": [
            {
              "@type": "ListItem",
              "position": 1,
              "name": "Home",
              "item": "https://vogo.family/"
            },
            {
              "@type": "ListItem",
              "position": 2,
              "name": "Magazin",
              "item": "https://vogo.family/shop/"
            },
            {
              "@type": "ListItem",
              "position": 3,
              "name": "Vaslui &#8211; Proxima Shopping Center"
            }
          ]
        },
        {
          "@type": "WebSite",
          "@id": "https://vogo.family/#website",
          "url": "https://vogo.family/",
          "name": "Vogo Family",
          "description": "",
          "potentialAction": [
            {
              "@type": "SearchAction",
              "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://vogo.family/?s={search_term_string}"
              },
              "query-input": {
                "@type": "PropertyValueSpecification",
                "valueRequired": true,
                "valueName": "search_term_string"
              }
            }
          ],
          "inLanguage": "en-US"
        }
      ]
    }
  },
  "jetpack_sharing_enabled": true,
  "_links": {
    "self": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/products/32671",
        "targetHints": {
          "allow": [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE"
          ]
        }
      }
    ],
    "collection": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/products"
      }
    ]
  }
}
```

#### Restaurants
- Method: GET
- Endpoint: `products`
#### Mall Delivery
- Method: GET
- Endpoint: `products`
#### Alba Iulia Services
- Method: GET
- Endpoint: `products`
### Categories

#### List Categories
- Method: GET
- Endpoint: `products/categories`
- Response Structure:
```json
{
  "id": 563,
  "name": "Activitati copii in orasul tau",
  "slug": "activitati-copii-in-orasul-tau",
  "parent": 228,
  "description": "Activitati copii in orasul tau",
  "display": "default",
  "image": {
    "id": 14014,
    "date_created": "2025-03-22T10:12:32",
    "date_created_gmt": "2025-03-22T08:12:32",
    "date_modified": "2025-03-22T10:12:42",
    "date_modified_gmt": "2025-03-22T08:12:42",
    "src": "https://vogo.family/wp-content/uploads/2025/03/kids-tabara-copii-.jpeg",
    "name": "kids-tabara-copii-activitati",
    "alt": ""
  },
  "menu_order": 173,
  "count": 1,
  "yoast_head": "<!-- This site is optimized with the Yoast SEO plugin v24.8.1 - https://yoast.com/wordpress/plugins/seo/ -->\n<title>Activitati copii in orasul tau Archives - Vogo Family</title>\n<!-- Admin only notice: this page does not show a meta description because it does not have one, either write it for this page specifically or go into the [Yoast SEO - Settings] menu and set up a template. -->\n<meta name=\"robots\" content=\"index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1\" />\n<link rel=\"canonical\" href=\"https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:locale\" content=\"en_US\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:type\" content=\"article\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:title\" content=\"Activitati copii in orasul tau Archives - Vogo Family\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:description\" content=\"Activitati copii in orasul tau\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:url\" content=\"https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/\" class=\"yoast-seo-meta-tag\" />\n<meta property=\"og:site_name\" content=\"Vogo Family\" class=\"yoast-seo-meta-tag\" />\n<meta name=\"twitter:card\" content=\"summary_large_image\" class=\"yoast-seo-meta-tag\" />\n<script type=\"application/ld+json\" class=\"yoast-schema-graph\">{\"@context\":\"https://schema.org\",\"@graph\":[{\"@type\":\"CollectionPage\",\"@id\":\"https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/\",\"url\":\"https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/\",\"name\":\"Activitati copii in orasul tau Archives - Vogo Family\",\"isPartOf\":{\"@id\":\"https://vogo.family/#website\"},\"breadcrumb\":{\"@id\":\"https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/#breadcrumb\"},\"inLanguage\":\"en-US\"},{\"@type\":\"BreadcrumbList\",\"@id\":\"https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/#breadcrumb\",\"itemListElement\":[{\"@type\":\"ListItem\",\"position\":1,\"name\":\"Home\",\"item\":\"https://vogo.family/\"},{\"@type\":\"ListItem\",\"position\":2,\"name\":\"Educa\u021bional-copii\",\"item\":\"https://vogo.family/product-category/educational-kids/\"},{\"@type\":\"ListItem\",\"position\":3,\"name\":\"Activitati copii in orasul tau\"}]},{\"@type\":\"WebSite\",\"@id\":\"https://vogo.family/#website\",\"url\":\"https://vogo.family/\",\"name\":\"Vogo Family\",\"description\":\"\",\"potentialAction\":[{\"@type\":\"SearchAction\",\"target\":{\"@type\":\"EntryPoint\",\"urlTemplate\":\"https://vogo.family/?s={search_term_string}\"},\"query-input\":{\"@type\":\"PropertyValueSpecification\",\"valueRequired\":true,\"valueName\":\"search_term_string\"}}],\"inLanguage\":\"en-US\"}]}</script>\n<!-- / Yoast SEO plugin. -->",
  "yoast_head_json": {
    "title": "Activitati copii in orasul tau Archives - Vogo Family",
    "robots": {
      "index": "index",
      "follow": "follow",
      "max-snippet": "max-snippet:-1",
      "max-image-preview": "max-image-preview:large",
      "max-video-preview": "max-video-preview:-1"
    },
    "canonical": "https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/",
    "og_locale": "en_US",
    "og_type": "article",
    "og_title": "Activitati copii in orasul tau Archives - Vogo Family",
    "og_description": "Activitati copii in orasul tau",
    "og_url": "https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/",
    "og_site_name": "Vogo Family",
    "twitter_card": "summary_large_image",
    "schema": {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "CollectionPage",
          "@id": "https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/",
          "url": "https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/",
          "name": "Activitati copii in orasul tau Archives - Vogo Family",
          "isPartOf": {
            "@id": "https://vogo.family/#website"
          },
          "breadcrumb": {
            "@id": "https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/#breadcrumb"
          },
          "inLanguage": "en-US"
        },
        {
          "@type": "BreadcrumbList",
          "@id": "https://vogo.family/product-category/educational-kids/activitati-copii-in-orasul-tau/#breadcrumb",
          "itemListElement": [
            {
              "@type": "ListItem",
              "position": 1,
              "name": "Home",
              "item": "https://vogo.family/"
            },
            {
              "@type": "ListItem",
              "position": 2,
              "name": "Educa\u021bional-copii",
              "item": "https://vogo.family/product-category/educational-kids/"
            },
            {
              "@type": "ListItem",
              "position": 3,
              "name": "Activitati copii in orasul tau"
            }
          ]
        },
        {
          "@type": "WebSite",
          "@id": "https://vogo.family/#website",
          "url": "https://vogo.family/",
          "name": "Vogo Family",
          "description": "",
          "potentialAction": [
            {
              "@type": "SearchAction",
              "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://vogo.family/?s={search_term_string}"
              },
              "query-input": {
                "@type": "PropertyValueSpecification",
                "valueRequired": true,
                "valueName": "search_term_string"
              }
            }
          ],
          "inLanguage": "en-US"
        }
      ]
    }
  },
  "_links": {
    "self": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/products/categories/563",
        "targetHints": {
          "allow": [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE"
          ]
        }
      }
    ],
    "collection": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/products/categories"
      }
    ],
    "up": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/products/categories/228"
      }
    ]
  }
}
```

#### Restaurant Category
- Method: GET
- Endpoint: `products/categories`
### Orders

#### List Orders
- Method: GET
- Endpoint: `orders`
- Response Structure:
```json
{
  "id": 33124,
  "parent_id": 0,
  "status": "processing",
  "currency": "RON",
  "version": "9.5.2",
  "prices_include_tax": false,
  "date_created": "2025-04-16T20:50:40",
  "date_modified": "2025-04-16T20:50:51",
  "discount_total": "0.00",
  "discount_tax": "0.00",
  "shipping_total": "30.00",
  "shipping_tax": "0.00",
  "cart_tax": "0.00",
  "total": "518.90",
  "total_tax": "0.00",
  "customer_id": 1,
  "order_key": "wc_order_CFcrRkikKVwpz",
  "billing": {
    "first_name": "vogo",
    "last_name": "family",
    "company": "",
    "address_1": "123",
    "address_2": "fres",
    "city": "Bucharest",
    "state": "BC",
    "postcode": "303494",
    "country": "RO",
    "email": "tanwardurgesh@gmail.com",
    "phone": "1223456"
  },
  "shipping": {
    "first_name": "vogo",
    "last_name": "family",
    "company": "",
    "address_1": "123",
    "address_2": "fres",
    "city": "Bucharest",
    "state": "BC",
    "postcode": "303494",
    "country": "RO",
    "phone": ""
  },
  "payment_method": "cod",
  "payment_method_title": "Cash on delivery",
  "transaction_id": "",
  "customer_ip_address": "2405:201:5c1b:68b6:850a:c5f0:9e16:c2e5",
  "customer_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
  "created_via": "checkout",
  "customer_note": "",
  "date_completed": null,
  "date_paid": null,
  "cart_hash": "293781212b02c3807999b74337911fcc",
  "number": "33124",
  "meta_data": [
    {
      "id": 1171,
      "key": "_billing_vat_code",
      "value": "123"
    },
    {
      "id": 1186,
      "key": "_googlesitekit_ga_purchase_event_tracked",
      "value": "1"
    },
    {
      "id": 1184,
      "key": "_wc_order_attribution_device_type",
      "value": "Desktop"
    },
    {
      "id": 1176,
      "key": "_wc_order_attribution_referrer",
      "value": "https://www.google.com/"
    },
    {
      "id": 1182,
      "key": "_wc_order_attribution_session_count",
      "value": "35"
    },
    {
      "id": 1179,
      "key": "_wc_order_attribution_session_entry",
      "value": "https://vogo.family/?page_id=32854&preview=true"
    },
    {
      "id": 1181,
      "key": "_wc_order_attribution_session_pages",
      "value": "17"
    },
    {
      "id": 1180,
      "key": "_wc_order_attribution_session_start_time",
      "value": "2025-04-12 10:14:34"
    },
    {
      "id": 1175,
      "key": "_wc_order_attribution_source_type",
      "value": "organic"
    },
    {
      "id": 1183,
      "key": "_wc_order_attribution_user_agent",
      "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    },
    {
      "id": 1178,
      "key": "_wc_order_attribution_utm_medium",
      "value": "organic"
    },
    {
      "id": 1177,
      "key": "_wc_order_attribution_utm_source",
      "value": "google"
    },
    {
      "id": 1172,
      "key": "is_vat_exempt",
      "value": "no"
    },
    {
      "id": 1185,
      "key": "wcal_abandoned_cart_id",
      "value": "749"
    }
  ],
  "line_items": [
    {
      "id": 200,
      "name": "Miercurea Ciuc - Nest Park Retail",
      "product_id": 32673,
      "variation_id": 0,
      "quantity": 1,
      "tax_class": "",
      "subtotal": "99.00",
      "subtotal_tax": "0.00",
      "total": "99.00",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": [],
      "sku": "67fc57f9e493",
      "price": 99,
      "image": {
        "id": "",
        "src": ""
      },
      "parent_name": null
    },
    {
      "id": 201,
      "name": "T\u00e2rgu Mure\u0219 - Mure\u0219 Mall",
      "product_id": 32657,
      "variation_id": 0,
      "quantity": 1,
      "tax_class": "",
      "subtotal": "99.00",
      "subtotal_tax": "0.00",
      "total": "99.00",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": [],
      "sku": "2dd4802e14de",
      "price": 99,
      "image": {
        "id": "",
        "src": ""
      },
      "parent_name": null
    },
    {
      "id": 202,
      "name": "Pite\u0219ti - Vivo Pite\u0219ti",
      "product_id": 32633,
      "variation_id": 0,
      "quantity": 1,
      "tax_class": "",
      "subtotal": "99.00",
      "subtotal_tax": "0.00",
      "total": "99.00",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": [],
      "sku": "edc0cecc643d",
      "price": 99,
      "image": {
        "id": "",
        "src": ""
      },
      "parent_name": null
    },
    {
      "id": 203,
      "name": "KETO meniu stil Szechuan 255g",
      "product_id": 32412,
      "variation_id": 0,
      "quantity": 1,
      "tax_class": "",
      "subtotal": "40.70",
      "subtotal_tax": "0.00",
      "total": "40.70",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": [],
      "sku": "5903933643892",
      "price": 40.7,
      "image": {
        "id": "27765",
        "src": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Keto-Meniu-Szechuan-4.jpg?fit=1000%2C1000&ssl=1"
      },
      "parent_name": null
    },
    {
      "id": 204,
      "name": "Bio Spirulina + Chlorella Diet-Food - 375 tablete x 400mg - 150g",
      "product_id": 32384,
      "variation_id": 0,
      "quantity": 1,
      "tax_class": "",
      "subtotal": "104.50",
      "subtotal_tax": "0.00",
      "total": "104.50",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": [],
      "sku": "5906395147649",
      "price": 104.5,
      "image": {
        "id": "27969",
        "src": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/Spirulina-Chlorella-1.jpg?fit=1000%2C1000&ssl=1"
      },
      "parent_name": null
    },
    {
      "id": 205,
      "name": "Paste Ramen Bio tip Soba 100% hrisca 280g",
      "product_id": 32408,
      "variation_id": 0,
      "quantity": 1,
      "tax_class": "",
      "subtotal": "46.70",
      "subtotal_tax": "0.00",
      "total": "46.70",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": [],
      "sku": "5906660508243",
      "price": 46.7,
      "image": {
        "id": "27879",
        "src": "https://i0.wp.com/vogo.family/wp-content/uploads/2025/04/p_5_0_4_0_5040-Paste-Ramen-Bio-tip-Soba-100risca-280g-1.jpg?fit=1000%2C1000&ssl=1"
      },
      "parent_name": null
    }
  ],
  "tax_lines": [],
  "shipping_lines": [
    {
      "id": 206,
      "method_title": "Cargus Livrare la domiciliu",
      "method_id": "cargus",
      "instance_id": "4",
      "total": "30.00",
      "total_tax": "0.00",
      "taxes": [],
      "meta_data": []
    }
  ],
  "fee_lines": [],
  "coupon_lines": [],
  "refunds": [],
  "payment_url": "https://vogo.family/checkout/order-pay/33124/?pay_for_order=true&key=wc_order_CFcrRkikKVwpz",
  "is_editable": false,
  "needs_payment": false,
  "needs_processing": true,
  "date_created_gmt": "2025-04-16T18:50:40",
  "date_modified_gmt": "2025-04-16T18:50:51",
  "date_completed_gmt": null,
  "date_paid_gmt": null,
  "currency_symbol": "lei",
  "manual_notes": "Payment to be made upon delivery. Order status&hellip;",
  "payment_mode": "Cash on delivery",
  "order_coupon": "",
  "transport_info": "",
  "order_audit": "https://vogo.family/wp-admin/admin.php?page=order_audit&order_id=33124",
  "_links": {
    "self": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/orders/33124",
        "targetHints": {
          "allow": [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE"
          ]
        }
      }
    ],
    "collection": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/orders"
      }
    ],
    "customer": [
      {
        "href": "https://vogo.family/wp-json/wc/v3/customers/1"
      }
    ]
  }
}
```

