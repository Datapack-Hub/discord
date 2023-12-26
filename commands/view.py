import disnake
from disnake.ext import commands
from io import BytesIO
import zipfile


class ViewFileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Quick Look")
    async def quicklook(self, inter: disnake.MessageCommandInteraction):
        if inter.target.attachments.__len__() == 0:
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
                    zip_file.filelist
                    if not file_info.is_dir() and not "__MACOSX" in file_info.filename:
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
            await inter.response.send_message(embed=emb, view=DropdownView(files_out))
        elif file.content_type == "text/plain" or file.content_type is None:
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
        await inter.response.send_message("Loading...", ephemeral=True)
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
                await inter.message.edit(embed=emb)
                await inter.delete_original_response()


class DropdownView(disnake.ui.View):
    def __init__(self, files):
        super().__init__()

        self.add_item(Dropdown(files))
