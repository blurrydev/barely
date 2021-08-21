"""
auto-generate lots of SEO-relevant tags

...because doing it manually is boring.
"""
from barely.plugins import PluginBase


class AutoSEO(PluginBase):

    def __init__(self):
        super().__init__()
        standard_config = {
            "PRIORITY": 30,
            "KEYWORD_MODE": "append",
            "AUTO_KEYWORDS": True
        }
        try:
            self.plugin_config = standard_config | self.config["AUTO_SEO"]
        except KeyError:
            self.plugin_config = standard_config

    def register(self):
        return "AutoSEO", self.plugin_config["PRIORITY"], ["yaml", self.config["PAGE_EXT"]]

    def action(self, *args, **kwargs):
        if "item" in kwargs:
            item = kwargs["item"]

            try:
                page_seo = item["meta"]["SEO"]
            except KeyError:
                page_seo = {}

            # Page-specific metadata; already merged with global metadata in ProcessingPipeline!
            def get_page(tag, rebrand=None):
                rebrand = rebrand if rebrand else tag
                if tag in item["meta"]:
                    return {rebrand: item["meta"][tag]}
                return {}

            # Page & SEO specific metadata, can differ from page-specific one
            def get_seo(tag, rebrand=None):
                rebrand = rebrand if rebrand else tag
                if tag in page_seo:
                    return {rebrand: page_seo[tag]}
                return {}

            # keywords global | (auto | page)
            # an title site_title anhaengen
            # falls kein Bild: bild finden
            # an og:url destination anhaengen

            seo = {}

            # title
            seo |= get_page("title")
            # description
            seo |= get_page("site_description", "description") | get_page("summary", "description") | get_page("description")
            # robots
            seo |= {"robots": "all"} | get_page("robots")
            # keywords
            seo |= get_page("site_keywords")
            seo |= get_page("keywords")
            # favicon
            seo |= get_page("favicon")

            # og:title
            seo |= get_page("title", "og:title") | get_seo("title", "og:title")
            # og:description
            seo |= get_page("site_description", "og:description") | get_page("summary", "og:description") | get_page("description", "og:description") | get_seo("description", "og:description")
            # og:image
            seo |= get_page("title_image", "og:image") | get_seo("title_image", "og:image")
            # og:url
            seo |= get_page("site_url", "og:url")
            # og:site_name
            seo |= get_page("title", "og:site_name") | get_page("site_name", "og:site_name") | get_seo("site_name", "og:site_name")

            # twitter:image:alt
            seo |= get_page("site_description", "twitter:image:alt") | get_page("summary", "twitter:image:alt") | get_page("description", "twitter:image:alt") | get_seo("description", "twitter:image:alt") | get_page("title_image_alt", "twitter:image:alt") | get_seo("title_image_alt", "twitter:image:alt")
            # twitter:card
            seo |= {"twitter:card": "summary_card_large"} | get_page("twitter_card", "twitter:card") | get_seo("twitter_card", "twitter:card")
            # twitter:site
            seo |= get_page("twitter_site", "twitter:site") | get_seo("twitter_site", "twitter:site")
            # twitter:creator
            seo |= get_page("twitter_creator", "twitter:creator") | get_seo("twitter_creator", "twitter:creator")

            yield item

    def finalize(self):
        # robots.txt
        # sitemap.txt
        pass
