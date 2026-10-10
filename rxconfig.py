import reflex as rx

from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
	app_name="reflex_databricks_demo",
	plugins=[rx.plugins.TailwindV3Plugin()],
	disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
