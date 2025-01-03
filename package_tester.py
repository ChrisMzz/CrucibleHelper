import cruciblehelper as ch
from pathlib import Path

# replace filepath with the correct path
# uses JK New Ingredients mod as an example : https://www.nexusmods.com/potioncraftalchemistsimulator/mods/18
filepath = r"D:\SteamLibrary\steamapps\common\Potion Craft\crucible\mods\JenkIngresMod_TS\package.yml"
file = Path(filepath)
p = ch.PackageReader(file)

page = "<head>\n"
page += f'<link rel="stylesheet" href="{Path(ch.__file__).parent/"webdisplay.css"}">'
page += "</head>\n"

page += "<body>\n"
page += p.draw_ingredients()
page += "</body>"

# writes html file with no style elements (will update to make it prettier)
with open(f"{file.stem}.html", "w") as fp:
    fp.write(page)
