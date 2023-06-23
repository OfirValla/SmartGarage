from discord_webhook import DiscordWebhook, DiscordEmbed

from Models.User import User

# ------------------------------------------------------------------ #

DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1121568312497815592/WPeizK4WAC7UjGhdUFtDbdL4ikpZc9r7P9dIP4Ltr7YPKD8i2hFHSHBkT6DlTVmrK7QK'

# ------------------------------------------------------------------ #

def send_discord_message(user: User, title: str, content: str):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK, username='GateController')
    
    webhook.avatar_url = user.photo
    embed = DiscordEmbed(title=title,
                         description=f'{user.name} ({user.email}) is {content}',
                         color='fff38e')
    webhook.add_embed(embed)

    webhook.execute()

# ------------------------------------------------------------------ #
