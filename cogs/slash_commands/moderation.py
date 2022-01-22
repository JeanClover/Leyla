import random

import disnake
from disnake.ext import commands


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def role_check(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member):
        if ctx.author.top_role.position <= member.top_role.position:
            return False

        elif ctx.author == member:
            return False
        
        else:
            return True

    @commands.slash_command(
        description="Можете теперь спокойно выдавать предупреждения uwu."
    )
    @commands.has_permissions(ban_members=True)
    async def warn(self, ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, *, reason: str = None):
        warn_id = random.randint(10000, 99999)
        embed = await self.bot.embeds.simple(thumbnail=ctx.author.display_avatar.url)
        embed.set_footer(text=f"ID: {warn_id} | {reason}")
        
        if await self.role_check(ctx, member):
            embed.description = f"**{member.name}** было выдано предупреждение"
            await self.bot.config.DB.moderation.insert_one({"_id": ctx.guild.id, "member": member.id, "reason": reason if reason else "Нет причины", "warn_id": warn_id})
        
        else:
            raise commands.MissingPermissions(missing_permissions=['ban_members'])

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))
