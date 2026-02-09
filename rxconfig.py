import reflex as rx

config = rx.Config(
	app_name="redis_browser",
	plugins=[rx.plugins.TailwindV3Plugin()],
	disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
