import discord

from io import BytesIO
import zipfile


class ViewFileCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="Quick Look")
    async def quicklook(self, inter: discord.ApplicationContext, message: discord.Message):
        if len(message.attachments) == 0:
            return await inter.response.send_message(
                "There is no file attached to this message!", ephemeral=True
            )
        file = message.attachments[0]
        if file.content_type == "application/zip":
            read_file = await file.read()

            files_out = []
            paths_out = ""
            amount = 0
            current = 0

            with zipfile.ZipFile(BytesIO(read_file), "r") as zip_file:
                for file_info in zip_file.infolist():
                    if not file_info.is_dir() and "__MACOSX" not in file_info.filename:
                        amount += 1
                        with zip_file.open(file_info.filename) as file:
                            current += 1
                            files_out.append(
                                {
                                    "path": file_info.filename,
                                    "content": file.read().decode(
                                        "utf-8", errors="ignore"
                                    ),
                                    "index": current,
                                }
                            )
                            paths_out += (
                                f"{current!s}: "
                                + file_info.filename.replace("/", " / ")
                                + "\n"
                            )

            emb = discord.Embed(
                title="Quick Look",
                description=f"All Files:\n```\n{paths_out}```",
                colour=discord.Colour.orange(),
            ).add_field(name="Total Files", value=str(amount))
            if len(files_out) > 25:
                await inter.response.send_message(
                    embed=emb, view=SelectView(files_out), ephemeral=True
                )
            else:
                await inter.response.send_message(
                    embed=emb, view=DropdownView(files_out), ephemeral=True
                )
        elif file.content_type is None or "text/plain" in file.content_type:
            formatting = "json"
            if file.filename.endswith("mcfunction"):
                formatting = "hs"
            file = await file.read()
            cont = file.decode()
            if len(cont) > 3050:
                cont = cont[0:3050] + "\n... this file is too long and has been truncated."
            emb = discord.Embed(
                title="Quick Look",
                description=f"```{formatting}\n{cont}```",
                colour=discord.Colour.orange(),
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
        else:
            await inter.response.send_message(
                f"Mimetype {file.content_type} is not supported!"
            )


class SelectView(discord.ui.View):
    def __init__(self, files):
        self.files = files
        super().__init__()

    @discord.ui.button(label="Open File", style=discord.ButtonStyle.blurple)
    async def confirm(
        self, button: discord.ui.Button, inter: discord.MessageInteraction
    ):
        await inter.response.send_modal(SelectModal(self.files))


class SelectModal(discord.ui.Modal):
    def __init__(self, files, *args, **kwargs) -> None:
        super().__init__(
            title="Open File", custom_id="mod_reason", *args, **kwargs
        )
        self.files = files
        self.add_item(discord.ui.InputText(
            label="ID",
            placeholder="28",
            custom_id="id"
        ))

    async def callback(self, inter: discord.Interaction) -> None:
        for i in self.files:
            if i["index"] == int(self.children[0].value.strip()):
                formatting = "json"
                if i["path"].endswith("mcfunction"):
                    formatting = "hs"
                
                if len(i["content"]) > 3050:
                    i["content"] = i["content"][0:3050] + "\n... this file is too long and has been truncated."
                emb = discord.Embed(
                    title="Quick Look",
                    description=f"`{i['path']}`:\n```{formatting}\n{i['content']}```",
                    colour=discord.Colour.orange(),
                )
                await inter.respond(embed=emb,ephemeral=True)

    async def on_error(self, error, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Oops, something went wrong.", ephemeral=True)
        print(error)

class Dropdown(discord.ui.Select):
    def __init__(self, files):
        self.files = files
        options = [
            discord.SelectOption(label=f"{i['index']!s}: {i['path']}") for i in files
        ]
        super().__init__(
            placeholder="Pick a file",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: discord.MessageInteraction):
        for i in self.files:
            if i["path"] == " ".join(self.values[0].split()[1:10000000]):
                formatting = "json"
                if i["path"].endswith("mcfunction"):
                    formatting = "hs"
                emb = discord.Embed(
                    title="Quick Look",
                    description=f"`{i['path']}`:\n```{formatting}\n{i['content']}```",
                    colour=discord.Colour.orange(),
                )
                await inter.respond(embed=emb, ephemeral=True)

class DropdownView(discord.ui.View):
    def __init__(self, files):
        super().__init__()
        
        self.add_item(Dropdown(files))
