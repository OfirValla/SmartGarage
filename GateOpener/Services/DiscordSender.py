from discord_webhook import DiscordWebhook, DiscordEmbed

# ------------------------------------------------------------------ #

DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1121568312497815592/WPeizK4WAC7UjGhdUFtDbdL4ikpZc9r7P9dIP4Ltr7YPKD8i2hFHSHBkT6DlTVmrK7QK'

# ------------------------------------------------------------------ #

def send_discord_message(title, content):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK, username='GateController')
    
    embed = DiscordEmbed(title=title,
                         description=content,
                         color='fff38e')
    webhook.add_embed(embed)

    webhook.execute()

# ------------------------------------------------------------------ #
