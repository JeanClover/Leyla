import platform
import sys
import re
from typing import Union
import random
from datetime import datetime

import disnake
import psutil
from disnake.ext import commands
from Tools.exceptions import CustomError


class MessageUtilities(commands.Cog, name='утилиты', description="Всякие ненужные, а может быть, и, вспомогательные команды"):

    def __init__(self, bot):
        self.bot = bot

    COG_EMOJI = '🔧'

    @commands.command(name="afk", description="Встали в афк? Ну ладно, подождём.", usage='afk [Причина]')
    async def message_utilities_afk_command(self, inter, *, reason: str = None):
        if await self.bot.config.DB.afk.count_documents({"guild": inter.guild.id, "member": inter.author.id}) == 0:
            await self.bot.config.DB.afk.insert_one({"guild": inter.guild.id, "member": inter.author.id,
                                                     "reason": reason if reason else "Без причины",
                                                     "time": datetime.now()})

        await inter.send(
            embed=await self.bot.embeds.simple(
                description=f"Я поставила вас в список AFK, ждём вашего возвращения :relaxed:\nПричина: {reason if reason else 'Без причины'}"
            )
        )

    @commands.command(name="stats", description="Статистика бота")
    async def message_utilities_stats(self, ctx):
        shard_names = {
            '0': 'Стелла',
            '1': 'Кристина',
            '2': 'Виктория',
            '3': 'Клэр'
        }
        guilds_info = (
            f"Количество серверов: **{len(self.bot.guilds)}**",
            f"Количество пользователей: **{len(self.bot.users)}**",
            f"Количество стикеров: **{len(self.bot.stickers)}**",
            f"Количество эмодзи: **{len(self.bot.emojis)}**",
        )
        about_me_info = (
            f"Я создана: **13 июля, 2021 года.**",
            f"[Мой сервер поддержки](https://discord.gg/43zapTjgvm)",
            f"Операционная система: **{platform.platform()}**",
            f"Язык программирования: **Python {sys.version}**"
        )
        other_info = (
            f"Мой ID: **{ctx.me.id}**",
            f"Количество слэш команд: **{len(self.bot.global_slash_commands)}**",
            f"Количество обычных команд: **{len([i for i in self.bot.commands if not i.name == 'jishaku' and not i.name == 'justify'])}**",
            f"Задержка: **{round(self.bot.latency*1000, 2)}ms**",
            f"RAM: **{psutil.virtual_memory().percent}%**",
            f"CPU: **{psutil.Process().cpu_percent()}%**",
            f"Кластеров: **{len(self.bot.shards)}**",
        )
        embed = await self.bot.embeds.simple(
            title=f"Моя статистика и информация обо мне | Кластер сервера: {shard_names[str(ctx.guild.shard_id)]}",
            description=f"Время, сколько я работаю - <t:{round(self.bot.uptime.timestamp())}:R> - ||спасите... ***моргнула 3 раза***||",
            url="https://leylabot.ml/",
            fields=[
                {"name": "Информация о серверах", "value": '\n'.join(guilds_info), "inline": True},
                {"name": "Информация про меня", "value": '\n'.join(about_me_info), "inline": True},
                {"name": "Всё прочее", "value": '\n'.join(other_info), "inline": True}
            ],
            footer={"text": f"Мои создатели: {', '.join([str(self.bot.get_user(i)) for i in self.bot.owner_ids])}", "icon_url": ctx.me.avatar.url}
        )

        await ctx.reply(embed=embed)
        

    @commands.group(name="profile", description="Информация о вас во мне, как бы странно это не звучало", invoke_without_command=True, usage="profile <Пользователь>")
    async def message_utilities_profile(self, ctx, user: disnake.User = None):
        user = ctx.author if not user else user

        if await self.bot.config.DB.badges.count_documents({"_id": user.id}) > 0:
            badge_data = ' '.join(dict(await self.bot.config.DB.badges.find_one({"_id": user.id}))['badges'])
        else:
            badge_data = 'Значков нет'
        
        level_data = await self.bot.config.DB.levels.find_one({"guild": ctx.guild.id})
        level_info = (
            f'Уровень: **{level_data["lvl"]}**',
            f'Опыт: **{level_data["xp"]} / {5*(level_data["lvl"]**2)+50*level_data["lvl"]+100}**'
        )

        fields = [
            {'name': 'Значки', 'value': badge_data, "inline": True},
            {'name': 'Уровни', 'value': '\n'.join(level_info), "inline": True}
        ]
        embed = await self.bot.embeds.simple(
            title=f'Профиль пользователя {user.id}',
            description=f"Статус **{user.name}** в боте: {'Просто пользователь' if not user.id in self.bot.owner_ids else 'Разработчик'}",
            fields=fields
        )

        await ctx.send(embed=embed)

    @commands.command(name='joke', description='Не смешно. Не смеёмся')
    async def message_utilities_joke(self, ctx):
        response = await self.bot.session.get(f'https://millionstatusov.ru/umor/page-{random.randint(1, 523)}.html')
        data = await response.read()

        data = data.decode('utf-8')
        quote = random.choice([i.strip() for i in re.findall(r'(?s)class="(?:t0|cont_text)">(.*?)<', data)])

        await ctx.reply(quote)

    @commands.command(
        name="idea", 
        description="Предложить идею, которая придёт на [сервер поддержки](https://discord.gg/43zapTjgvm)",
        usage="idea <Само сообщение>"
    )
    async def message_utilities_idea(self, ctx, *, text: str):
        channel = self.bot.get_channel(864408517237800980)
        message = await channel.send(f'Пришла новая идея от: **{ctx.author.name}**\nС сервера: **{ctx.guild.name}**\n\nСама идея: {text}')
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        channel: disnake.TextChannel = channel.history() 


def setup(bot):
    bot.add_cog(MessageUtilities(bot))
