import json
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')


try:
    with open('options.json', 'r', encoding='utf-8') as file:
        pass
except IOError:
    with open('options.json', 'w', encoding='utf-8') as file:
        file.write('{"options_channel": -1, "options_message": -1, "discussion_channel": -1, "common_channel": -1, "channels_category": -1}')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Among Us"))
    print("INFO : Le bot est démarré et prêt à l'utilisation !")


@bot.event
async def on_raw_reaction_add(payload):

    if not payload.member.bot:

        with open('options.json', 'r', encoding='utf-8') as file:
            config = json.load(file)

        if payload.message_id == config['options_message']:
            options_channel = discord.utils.get(payload.member.guild.text_channels, id=config['options_channel'])
            discussion_channel = discord.utils.get(payload.member.guild.text_channels, id=config['discussion_channel'])
            channels_category = discord.utils.get(payload.member.guild.categories, id=config['channels_category'])
            common_channel = discord.utils.get(payload.member.guild.voice_channels, id=config['common_channel'])

            if payload.emoji.name == 'ℹ️':
                message = await options_channel.send(f"Salut à toi {payload.member.mention}, je suis **DiscordAmongUs** !\nJ'ai été développé par **BidulaxStudio** et je suis toujours prêt à vous aider !\nMon préfixe de commande est **!** et ma latence actuelle est de **{round(bot.latency*100)}ms**.")
                await message.delete(5)

            elif payload.emoji.name == '👋':
                await discussion_channel.send(f"@here Le joueur {payload.member.mention} est prêt pour une partie !")

            elif payload.emoji.name == '📢':
                if payload.member.guild_permissions.administrator:
                    await discussion_channel.send("@everyone Démarrage d'une partie, rendez-vous dans le salon de jeu !")

            elif payload.emoji.name == '🔈':
                if payload.member.guild_permissions.administrator:
                    for member in list(common_channel.members):
                        await member.move_to(await channels_category.create_voice_channel(member.name))

            elif payload.emoji.name == '🔊':
                if payload.member.guild_permissions.administrator:
                    for channel in channels_category.voice_channels:
                        if not channel == common_channel:
                            for member in channel.members:
                                await member.move_to(common_channel)
                            await channel.delete()

            options_message = await options_channel.fetch_message(config['options_message'])
            for reaction in options_message.reactions:
                if reaction.count > 1:
                    await reaction.remove(payload.member)


@commands.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, options_channel: discord.TextChannel, discussion_channel: discord.TextChannel, common_channel: discord.VoiceChannel):
    options_embed = discord.Embed(title="Options & Commandes")
    options_embed.add_field(name='Joueurs', value="ℹ️ Obtenez les informations du bot\n👋 Signalez que vous êtes prêts pour une partie", inline=False)
    options_embed.add_field(name='Gérants', value="📢 Annoncez le démarrage d'une partie\n🔈 Séparez les joueurs dans les salons\n🔊 Remettez les joueurs ensemble", inline=False)
    options_message = await options_channel.send(embed=options_embed)
    await options_message.add_reaction('ℹ️')
    await options_message.add_reaction('👋')
    await options_message.add_reaction('📢')
    await options_message.add_reaction('🔈')
    await options_message.add_reaction('🔊')

    with open('options.json', 'w', encoding='utf-8') as file:
        json.dump({"options_channel": options_channel.id,
                   "options_message": options_message.id,
                   "discussion_channel": discussion_channel.id,
                   "common_channel": common_channel.id,
                   "channels_category": common_channel.category_id},
                  file)

    await ctx.send(f"{ctx.author.mention} Vous avez mis en place le bot !")


@commands.command()
async def status(ctx, type: str = 'watching', *, status: str = 'Among Us'):
    if ctx.author.id == ctx.guild.owner_id:
        available_activities = ['playing', 'listening', 'watching']
        if type in available_activities:
            if type == 'playing':
                activity = discord.Activity(type=discord.ActivityType.playing, name=status)
            elif type == 'listening':
                activity = discord.Activity(type=discord.ActivityType.listening, name=status)
            else:
                activity = discord.Activity(type=discord.ActivityType.watching, name=status)
            await bot.change_presence(activity=activity)
            await ctx.send(f"{ctx.author.mention} Le status du bot a bien été changé !")
        else:
            await ctx.send(f"{ctx.author.mention} Les types d'activités disponibles sont {available_activities} !")


bot.add_command(setup)
bot.add_command(status)


bot.run('The token of the bot !')
