import disnake
from disnake.ext import commands
from io import BytesIO
import zipfile


class ViewFileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Quick Look")
    async def quicklook(self, inter: disnake.MessageCommandInteraction):
        if len(inter.target.attachments) == 0:
            return await inter.response.send_message(
                "There is no file attached to this message!", ephemeral=True
            )
        file = inter.target.attachments[0]
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

            emb = disnake.Embed(
                title="Quick Look",
                description=f"All Files:\n```\n{paths_out}```",
                color=disnake.Color.orange(),
            ).add_field("Total Files", str(amount))
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
            emb = disnake.Embed(
                title="Quick Look",
                description=f"```{formatting}\n{file.decode()}```",
                color=disnake.Color.orange(),
            )
            await inter.response.send_message(embed=emb)
        else:
            await inter.response.send_message(
                f"Mimetype {file.content_type} is not supported!"
            )


class SelectView(disnake.ui.View):
    def __init__(self, files):
        self.files = files
        super().__init__()

    @disnake.ui.button(label="Open File", style=disnake.ButtonStyle.blurple)
    async def confirm(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        await inter.response.send_modal(SelectModal(self.files))


class SelectModal(disnake.ui.Modal):
    def __init__(self, files) -> None:
        self.files = files
        components = [
            disnake.ui.TextInput(
                label="ID",
                placeholder="28",
                custom_id="id",
                style=disnake.TextInputStyle.short,
            ),
        ]
        super().__init__(
            title="Open File", custom_id="mod_reason", components=components
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.defer(ephemeral=True)
        for i in self.files:
            if i["index"] == int(inter.text_values["id"].strip()):
                formatting = "json"
                if i["path"].endswith("mcfunction"):
                    formatting = "hs"
                emb = disnake.Embed(
                    title="Quick Look",
                    description=f"`{i['path']}`:\n```{formatting}\n{i['content']}```",
                    color=disnake.Color.orange(),
                )
                await inter.send(embed=emb,ephemeral=True)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.channel.send(
            f"Oops, something went wrong. `{' '.join(error.args)}`"
        )


class Dropdown(disnake.ui.StringSelect):
    def __init__(self, files):
        self.files = files
        options = [
            disnake.SelectOption(label=f"{i['index']!s}: {i['path']}") for i in files
        ]
        super().__init__(
            placeholder="Pick a file",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer(ephemeral=True)
        for i in self.files:
            if i["path"] == " ".join(self.values[0].split()[1:10000000]):
                formatting = "json"
                if i["path"].endswith("mcfunction"):
                    formatting = "hs"
                emb = disnake.Embed(
                    title="Quick Look",
                    description=f"`{i['path']}`:\n```{formatting}\n{i['content']}```",
                    color=disnake.Color.orange(),
                )
                await inter.edit_original_message(embed=emb)


class DropdownView(disnake.ui.View):
    def __init__(self, files):
        super().__init__()

        self.add_item(Dropdown(files))
