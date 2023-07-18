from discord_webhook import DiscordWebhook, DiscordEmbed

from Models.User import User

import os

# ------------------------------------------------------------------ #

DISCORD_WEBHOOK: str = os.getenv('DISCORD_WEBHOOK')

# ------------------------------------------------------------------ #

def send_discord_message(user: User, title: str, content: str) -> None:
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK, username='GateController')
    
    webhook.avatar_url = user.photo
    embed = DiscordEmbed(title=title,
                         description=f'{user.name} ({user.email}) is {content}',
                         color='fff38e')
    webhook.add_embed(embed)

    webhook.execute()

# ------------------------------------------------------------------ #
