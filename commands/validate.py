import disnake
from disnake.ext import commands
from io import BytesIO
import zipfile
import json


class ValidateFileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Validate Datapack")
    async def quicklook(self, inter: disnake.MessageCommandInteraction):
        issues = []
        if len(inter.target.attachments) == 0:
            return await inter.response.send_message(
                "There is no file attached to this message!", ephemeral=True
            )
        file = inter.target.attachments[0]
        if file.content_type == "application/zip":
            await inter.response.defer()
            read_file = await file.read()

            with zipfile.ZipFile(BytesIO(read_file), "r") as zip_file:
                if "pack.mcmeta" not in zip_file.namelist():
                    issues.append(
                        "I couldn't find `pack.mcmeta`. Make sure that it exists in the root of the zip."
                    )

                if not any(s.startswith("data/") for s in zip_file.namelist()):
                    issues.append(
                        "I couldn't find the folder `data`. Make sure that it exists in the root of the zip."
                    )

                if not any(
                    s.startswith("data/minecraft/") for s in zip_file.namelist()
                ):
                    issues.append(
                        "I couldn't find the namespace `minecraft`. It isn't required, but 90% of datpacks do need to have it. If you don't use tick/load functions or you don't need to change vanilla data, then disregard this."
                    )

                namespaces = []

                for file_info in zip_file.infolist():
                    if not file_info.is_dir():
                        if file_info.filename.endswith(".mcfunction.txt"):
                            issues.append(
                                f"The file at path `{file_info.filename}` has not been saved correctly. You have saved it as a `.mcfunction.txt` instead of just `.mcfunction`. This is likely due to File Name Extensions not being visible in your file explorer."
                            )
                        if file_info.filename.endswith(".json.txt"):
                            issues.append(
                                f"The file at path `{file_info.filename}` has not been saved correctly. You have saved it as a `.json.txt` instead of just `.json`. This is likely due to File Name Extensions not being visible in your file explorer."
                            )
                        if file_info.filename.endswith(".jason"):
                            issues.append(
                                f"Who's Jason? The file at path `{file_info.filename}` has been saved as a `.jason` file instead of `.json`."
                            )
                        if file_info.filename.endswith(".json"):
                            with zip_file.open(file_info, "r") as json_file:
                                try:
                                    # not sure what this is for or if it's needed, 
                                    # but its unused and vscode isn't liking it
                                    # sincerely, me
                                    this = json.load(json_file)
                                except json.JSONDecodeError:
                                    issues.append(
                                        f"The JSON file at path `{file_info.filename}` uses incorrect syntax"
                                    )
                        if " " in file_info.filename.split("/")[-1]:
                            issues.append(
                                f"The filename of the file at path `{file_info.filename}` contains spaces. In a datapack, no files can have spaces in the names."
                            )
                        if any(
                            char.isupper() for char in file_info.filename.split("/")[-1]
                        ):
                            issues.append(
                                f"The filename of the file at path `{file_info.filename}` contains a capital letter. In a datapack, no files can have capital letters in the names."
                            )

                        if len(file_info.filename.split("/")) > 1:
                            if file_info.filename.split("/")[1] not in namespaces:
                                namespaces.append(file_info.filename.split("/")[1])
                for namespace in namespaces:
                    if any(char.isupper() for char in namespace):
                        issues.append(
                            f"The namespace `{namespace}` contains a capital letter. Namespaces can't have capital letters."
                        )
                    if " " in namespace:
                        issues.append(
                            f"The namespace `{namespace}` contains a space. Namespaces can't have spaces."
                        )

            embed = disnake.Embed(title="Result of analysis")

            if len(issues) > 0:
                text_issues = ""
                for issue in issues:
                    text_issues += f"- {issue}\n"
                embed.description = f"I found {len(issues)!s} issues with the structure of your datapack.\n{text_issues}"
                embed.color = disnake.Color.red()
            else:
                embed.description = (
                    "I found no issues with the structure of your datapack."
                )
                embed.color = disnake.Color.green()

            await inter.edit_original_message(embed=embed)

        else:
            await inter.response.send_message("This is not a ZIP file!", ephemeral=True)
