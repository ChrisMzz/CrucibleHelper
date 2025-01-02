from cruciblehelper import *
from pathlib import Path

# replace filepath with the correct path
# uses JK New Ingredients mod as an example : https://www.nexusmods.com/potioncraftalchemistsimulator/mods/18
filepath = r"D:\SteamLibrary\steamapps\common\Potion Craft\crucible\mods\JenkIngresMod_TS\package.yml"
file = Path(filepath)
p = PackageReader(file)

outputs = [[draw_call.svg for stack in ingredient.draw_stack_items() for draw_call in stack] + [ingredient.draw_path()] for ingredient in p.ingredients ]

body = "<table>"+ "".join(["<tr><td><table><tr>" + "".join([f"<td>{o}</td>" for o in output[:-1]]) + "</tr></table></td>" + f"<td>{output[-1]}</td>" +"</tr>" for output in outputs])+"</table>"

# writes html file with no style elements (will update to make it prettier)
with open(f"{file.stem}.html", "w") as fp:
    fp.write(body)
