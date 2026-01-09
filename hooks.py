import datetime

def on_config(config):
    # Replace the placeholder {year} with the current year
    if config.copyright:
        config.copyright = config.copyright.replace("{year}", str(datetime.date.today().year))
    return config