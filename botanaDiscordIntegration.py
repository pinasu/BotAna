import discord, sys, asyncio

def notify_live(TOKEN, liveTitle, channel_name):
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = discord.Client()

    @client.event
    async def on_ready():
        msg = liveTitle+' https://www.twitch.tv/'+channel_name+' @here'
        await client.send_message(list(client.get_all_channels())[1], msg)

    client.run(TOKEN)
