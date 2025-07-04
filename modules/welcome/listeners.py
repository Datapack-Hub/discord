import discord

import variables
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
import io

async def get_member_join_card(user, self):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    directory = os.getcwd()

    background_path = os.path.join(directory, "files", "background.png")
    pfp_path = await user.display_avatar.read()
    font_path = os.path.join(directory, "files", "Lexend-Black.ttf")
    output_path = os.path.join(directory, "files", "output.png")

    pfp_image = Image.open(io.BytesIO(pfp_path))
    background_image = Image.open(background_path).convert("RGBA")
    font_path = font_path
    font = ImageFont.truetype(font_path, size=80)
    font_2 = ImageFont.truetype(font_path, size=40)

    if user.global_name:
        name = user.global_name
    else:
        name = user.name

    guild = self.bot.get_guild(variables.guild)
    member_count = guild.member_count

    blur_radius = 0
    offset = 4

    back_colour = Image.new("RGBA", pfp_image.size, (0, 0, 0, 0))
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pfp_image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (offset, offset, pfp_image.size[0] - offset, pfp_image.size[1] - offset),
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    pfp_image_round = Image.composite(pfp_image, back_colour, mask)
    pfp_image_round = pfp_image_round.resize((180, 180), Image.Resampling.LANCZOS)
    background_pfp = background_image.convert("RGBA")

    draw = ImageDraw.Draw(background_pfp)
    background_pfp.paste(pfp_image_round, (45, 50), pfp_image_round)

    width = draw.textlength(name, font=font)
    bbox = draw.textbbox((1, 1), name, font=font)
    height = bbox[3] - bbox[1]
    if width > 634:
        for i in range(0, int(width)):
            width = draw.textlength(
                name, font=ImageFont.truetype(font_path, size=80 - i)
            )
            if width <= 634:
                bbox = draw.textbbox(
                    (1, 1),
                    name.replace("y", "").replace("g", "").replace("j", "").replace("(", "").replace(")", "").replace("/", ""),
                    font=ImageFont.truetype(font_path, size=80 - i),
                )
                height = bbox[3] - bbox[1]

                draw.text(
                    ((265 + (581 / 2) - (width / 2) + 10), 87 + 61 - height),
                    name,
                    font=ImageFont.truetype(font_path, size=80 - i),
                    fill=(255, 99, 26),
                )
                break
    else:
        draw.text(
            ((265 + (581 / 2) - (width / 2) + 10), 87),
            name,
            font=font,
            fill=(255, 99, 26),
        )

    width = draw.textlength("Member #" + str(member_count), font=font_2)
    bbox = draw.textbbox((1, 1), "Member #" + str(member_count), font=font_2)
    height = bbox[3] - bbox[1]
    draw.text(
        ((265 + (581 / 2) - (width / 2)), 187),
        "Member #" + str(member_count),
        font=font_2,
        fill=(255, 166, 74),
    )

    background_pfp.save(output_path)


class WelcomeListeners(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(variables.new_member_channel)
        
        if channel is None:
            return
        
        await get_member_join_card(member, self)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        directory = os.getcwd()
        await channel.send(
            # content=random.choice(welcome_messages) % member.name,
            file=discord.File(os.path.join(directory, "files", "output.png")),
            allowed_mentions=discord.AllowedMentions.none()
        )
        
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == variables.intro and not message.author.bot:
            # Add reaction
            await message.add_reaction("👋")
            
            # Delete past bot message
            def is_user(m: discord.Message):
                if m.author.id != self.bot.user.id:
                    return False
                return True

            await message.channel.purge(limit=10, check=is_user)
            
            # Post new bot message
            embed = discord.Embed(
                title="👋 Introduce yourself to the community!",
                description="This is your chance to make yourself known. Tell us a bit about yourself:\n- your past experiences with datapacks\n- how you found Datapack Hub\n- some facts about yourself\nThen, come say hi in our general chat!",
                color=discord.Colour.orange()
            )
            
            await message.channel.send(embed=embed)