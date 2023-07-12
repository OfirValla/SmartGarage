from discord_webhook import DiscordWebhook, DiscordEmbed
import os

# ------------------------------------------------------------------ #

DISCORD_WEBHOOK: str = os.getenv('DISCORD_WEBHOOK')

# ------------------------------------------------------------------ #

def send_discord_message(status: str, confidence, image) -> None:
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK, username='GateAI')
    webhook.add_file(file=image, filename='gate.jpg')

    embed = DiscordEmbed(title=f'Gate Status', color='fff38e')
    embed.add_embed_field('Status', status, inline= False)
    embed.add_embed_field('Confidence', f'{confidence}%', inline= False)
    embed.set_thumbnail(url='attachment://gate.jpg')
    webhook.add_embed(embed)

    webhook.execute()

# ------------------------------------------------------------------ #
