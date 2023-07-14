from discord_webhook import DiscordWebhook, DiscordEmbed

from Models.Status import Status

from datetime import datetime
import os

# ------------------------------------------------------------------ #

DISCORD_WEBHOOK: str = os.getenv('DISCORD_WEBHOOK')

# ------------------------------------------------------------------ #

def send_log_message(msg: str) -> None:
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK, username='GateAI')

    embed = DiscordEmbed(title=f'Gate Status', color='22ad15')
    embed.add_embed_field('Time', str(datetime.now()))
    embed.add_embed_field('Log', msg, inline= False)
    webhook.add_embed(embed)

    webhook.execute()

# ------------------------------------------------------------------ #

def send_status_update(status: Status, image) -> None:
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK, username='GateAI')
    webhook.add_file(file=image, filename='gate.jpg')

    embed = DiscordEmbed(title=f'Gate Status', color='fff38e')
    embed.add_embed_field('Status', status.current_status, inline= False)
    embed.add_embed_field('Confidence', f'{status.confidence_score}%', inline= False)
    embed.set_thumbnail(url='attachment://gate.jpg')
    webhook.add_embed(embed)

    webhook.execute()

# ------------------------------------------------------------------ #
