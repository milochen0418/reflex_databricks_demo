import reflex as rx

config = rx.Config(
	app_name="reflex_databricks_demo",
	plugins=[rx.plugins.TailwindV3Plugin()],
	disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
