from dataclasses import dataclass
import yaml
from pathlib import Path

def handle_collision(collision):
    if type(collision) == dict:
        return collision["data"]
    return collision

def handle_selfcollision(selfCollision, collision):
    if type(selfCollision) == str: return selfCollision
    if "data" in selfCollision.keys(): return selfCollision["data"]
    if "scale" in selfCollision.keys():
        sx, sy = selfCollision["scale"].split(",")
        sx, sy = float(sx), float(sy)
        if type(collision) == dict: collision : str = collision["data"]
        P1 = collision.split(" ")
        P2 = [float(p) for p in P1 if p not in ["M", "L"]]
        P3 = [p for p in P1 if p in ["M", "L"]]
        P4 = [[pml,px,py] for pml,px,py in zip(P3, [round(p*sx, 4) for p in P2[::2]], [round(p*sy, 4) for p in P2[1::2]])]
        return [str(p) for P in P4 for p in P]



@dataclass
class CollisionDrawer: 
    output_filename:str
    sprite:str
    collision:str
    selfCollision:str=""
    stroke:str="ff0000"

    @property
    def svg(self):
        output = f"""
        <svg height="50" width="50" viewBox="-1 -1 2 2" xmlns="http://www.w3.org/2000/svg">
        <image href="{self.sprite}" height="1.2" width="1.2" x="-0.6" y="-0.6"/>
        <path d="{self.collision} z"
        style="fill:#FFDDDDAA;;stroke:#{self.stroke};stroke-width:0.03" />"""
        if len(self.selfCollision)>0:
            output += f"""
            <path d="{self.selfCollision} z"
            style="fill:none;stroke:#{self.stroke[::-1]};stroke-width:0.03" />"""
        return output+"</svg>"
    
    def save(self):
        with open(f"{self.output_filename}.svg", "w") as fp:
            fp.write(self.svg)


class PackageReader:
    def __init__(self, file:Path):
        with open(file, 'r', encoding="utf8") as stream:
            data : dict = yaml.safe_load(stream)
        self.file = file
        self.name = data["name"]
        self.author = data["author"]
        self.version = data["version"]
        self.dependencies = data["dependencies"]
        if "ingredients" in data.keys():
            self.ingredients = [Ingredient(ingredient, file) for ingredient in data["ingredients"] ]
    
    def draw_ingredients(self):
        outputs = [[draw_call.svg for stack in ingredient.draw_stack_items() for draw_call in stack] + [ingredient.draw_path()] for ingredient in self.ingredients ]
        return "<table>"+ "".join(["<tr><td><table><tr>" + "".join([f"<td>{o}</td>" for o in output[:-1]]) + "</tr></table></td>" + f"<td>{output[-1]}</td>" +"</tr>" for output in outputs])+"</table>\n"


class Ingredient:
    def __init__(self, data:dict, file:Path):
        self.file = file
        self.name = data["name"]
        self.id = data["id"]
        self.description = "" if "description" not in data.keys() else data["description"]
        self.ingredientListIcon = None if "ingredientListIcon" not in data.keys() else data["ingredientListIcon"]
        self.inventoryImage = None if "inventoryImage" not in data.keys() else data["inventoryImage"]
        self.recipeStepImage = None if "recipeStepImage" not in data.keys() else data["recipeStepImage"]
        self.inheritFrom = "Waterbloom" if "inheritFrom" not in data.keys() else data["inheritFrom"]
        self.basePrice = None if "basePrice" not in data.keys() else data["basePrice"]
        self.stackItems : list[dict] = data["stackItems"]
        self.groundColor = data["groundColor"]
        self.soldBy = data["soldBy"]
        self.grindStartPercent = data["grindStartPercent"]
        self.isTeleportationIngredient = data["isTeleportationIngredient"]
        self.path = data["path"]
    
    def draw_stack_items(self, single=True) -> list[list[CollisionDrawer]]: 
        calls = []
        for stackItem in self.stackItems:
            if "selfCollision" in stackItem.keys():
                calls.append([CollisionDrawer(
                    output_filename=stackItem["sprite"], 
                    sprite=self.file.parent/stackItem["sprite"],
                    collision=handle_collision(stackItem["collision"]),
                    selfCollision=handle_selfcollision(stackItem["selfCollision"], stackItem["collision"]),
                    stroke=self.groundColor[1:]
                )])
            else:
                calls.append([CollisionDrawer(
                    output_filename=stackItem["sprite"], 
                    sprite=self.file.parent/stackItem["sprite"],
                    collision=handle_collision(stackItem["collision"]),
                    stroke=self.groundColor[1:]
                )])
            while "grindsInto" in stackItem.keys():
                stackItem:dict = stackItem["grindsInto"][0]
                if "selfCollision" in stackItem.keys():
                    calls[-1] += [CollisionDrawer(
                        output_filename=stackItem["sprite"], 
                        sprite=self.file.parent/stackItem["sprite"],
                        collision=handle_collision(stackItem["collision"]),
                        selfCollision=handle_selfcollision(stackItem["selfCollision"], stackItem["collision"]),
                        stroke=self.groundColor[1:]
                    )]
                else:
                    calls[-1] += [CollisionDrawer(
                        output_filename=stackItem["sprite"], 
                        sprite=self.file.parent/stackItem["sprite"],
                        collision=handle_collision(stackItem["collision"]),
                        stroke=self.groundColor[1:]
                    )]
            if single: break
        return calls
    
    def draw_path(self):
        path : str = self.path["data"]
        i, strokes = 0, path.split(" ")
        vals = []
        if "scale" in self.path.keys(): 
            sx, sy = self.path["scale"].split(",")
            sx, sy = float(sx), float(sy)
        else: sx, sy = 1, 1
        while i < len(strokes):
            v = strokes[i]
            if v == "L":
                x, y = strokes[i+1:i+3]
                i += 3
            if v == "C":
                x, y = strokes[i+5:i+7]
                i += 7
            vals.append(sx*float(x)), vals.append(sy*float(y))
        mx, Mx, my, My = min(vals[::2]), max(vals[::2]), min(vals[1::2]), max(vals[1::2])
        mx, my = min(0, mx), min(0, my)
        P1 = [float(p) for p in strokes if p not in ["C", "L"]]
        P2 = [str(p*(sx,sy)[k%2]) for k,p in enumerate(P1)]
        P3 = [p for p in strokes if p in ["C", "L"]]
        i, scaled_path = 0, []
        for p in P3:
            if p == 'C': scaled_path += ["C"] + P2[i:i+6]; i+=6
            if p == 'L': scaled_path += ["L"] + P2[i:i+2]; i+=2
        scaled_path = " ".join(scaled_path)
        return fr"""
        <svg height="50" width="50" viewBox="{ f"{mx-2} {my-2} {Mx-mx+4} {My-my+4}" }" xmlns="http://www.w3.org/2000/svg">
        <path d="m 0 0 {scaled_path}"
        style="fill:none;stroke:{self.groundColor};stroke-width:0.1" /></svg>"""


