import disnake
from disnake.ext import commands
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

    guild = self.bot.get_guild(935560260725379143)
    member_count = guild.member_count

    blur_radius = 0
    offset = 4

    back_color = Image.new("RGBA", pfp_image.size, (0, 0, 0, 0))
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pfp_image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (offset, offset, pfp_image.size[0] - offset, pfp_image.size[1] - offset),
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    pfp_image_round = Image.composite(pfp_image, back_color, mask)
    pfp_image_round = pfp_image_round.resize((180, 180), Image.LANCZOS)
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


class OnMemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        channel = self.bot.get_channel(variables.new_member_channel)
        await get_member_join_card(member, self)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        directory = os.getcwd()
        await channel.send(
            file=disnake.File(os.path.join(directory, "files", "output.png"))
        )
