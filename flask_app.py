import yaml
import pyrsistent
from flask import Flask
from flask import render_template

app = Flask(__name__)


def format_prereq(r):
    for k, x in r.items():
        print(k)
        if "any" in x:
            x = x["any"]
        if "Attribute" in x:
            yield ", ".join(
                str(list(y.items())[0][0]) + ": " + str(list(y.items())[0][1])
                for y in x["Attribute"]
            )
        elif "Other" in x:
            yield ", ".join(x["Other"])
        else:
            yield x


class Bane(pyrsistent.PClass):
    name = pyrsistent.field(type=str, mandatory=True)
    tags = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    power_levels = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    attributes = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    attack = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    invocation_time = pyrsistent.field(type=str, mandatory=True)
    duration = pyrsistent.field(type=str, mandatory=True)
    description = pyrsistent.field(type=str, mandatory=True)
    effect = pyrsistent.field(type=str, mandatory=False)
    special = pyrsistent.field(type=str, mandatory=False)

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            tags=pyrsistent.pset(d["tags"]),
            power_levels=pyrsistent.pset(d["power"]),
            attributes=pyrsistent.pset(d["attackAttributes"]),
            attack=pyrsistent.pset(d["attack"]),
            invocation_time=d["invocationTime"],
            duration=d["duration"],
            description=d["description"].strip(),
            effect=d["effect"].strip(),
            special=d.get("special", "").strip(),
        )


class Boon(pyrsistent.PClass):
    name = pyrsistent.field(type=str, mandatory=True)
    tags = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    power_levels = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    attributes = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    invocation_time = pyrsistent.field(type=str, mandatory=True)
    duration = pyrsistent.field(type=str, mandatory=True)
    description = pyrsistent.field(type=str, mandatory=True)
    effect = pyrsistent.field(type=str, mandatory=False)
    special = pyrsistent.field(type=str, mandatory=False)

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            tags=pyrsistent.pset(d["tags"]),
            power_levels=pyrsistent.pset(d["power"]),
            attributes=pyrsistent.pset(d["attribute"]),
            invocation_time=d["invocationTime"],
            duration=d["duration"],
            description=d["description"].strip(),
            effect=d["effect"].strip(),
            special=d.get("special", "").strip(),
        )


class Feat(pyrsistent.PClass):
    name = pyrsistent.field(type=str, mandatory=True)
    tags = pyrsistent.field(type=pyrsistent.PSet, mandatory=True)
    prerequisites = pyrsistent.field(mandatory=True)
    cost = pyrsistent.field(type=int, mandatory=True)
    description = pyrsistent.field(type=str, mandatory=True)
    effect = pyrsistent.field(type=str, mandatory=True)
    special = pyrsistent.field(type=str, mandatory=False)

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            tags=pyrsistent.pset(d["tags"]),
            # TODO: translate {'tier1': {'Feat': ['Battle Trance']}}
            prerequisites=list(format_prereq(d["prerequisites"])),
            cost=d["cost"][0],
            description=d["description"].strip(),
            effect=d["effect"].strip(),
            special=d.get("special", "").strip(),
        )


with open("core-rules/banes/banes.yml", "rb") as f:
    banes = {
        bane["name"].lower(): Bane.from_dict(bane)
        for bane in yaml.load(f.read())
    }

with open("core-rules/boons/boons.yml", "rb") as f:
    boons = {
        boon["name"].lower(): Boon.from_dict(boon)
        for boon in yaml.load(f.read())
    }

with open("core-rules/feats/feats.yml", "rb") as f:
    feats = {
        feat["name"].lower(): Feat.from_dict(feat)
        for feat in yaml.load(f.read())
    }


@app.route("/banes")
def bane_index():
    return render_template(
        "bane-index.html", bane_names=[b.name for b in banes.values()]
    )


@app.route("/banes/<bane_name>")
def get_banes(bane_name):
    try:
        bane = banes[bane_name.lower()]
        return render_template(
            "banes.html",
            bane=bane,
            bane_names=[b.name for b in banes.values()],
        )
    except KeyError:
        return render_template("bane-not-found.html", bane=bane_name)


@app.route("/boons")
def boon_index():
    return render_template(
        "boon-index.html", boon_names=[b.name for b in boons.values()]
    )


@app.route("/boons/<boon_name>")
def get_boons(boon_name):
    try:
        boon = boons[boon_name.lower()]
        return render_template(
            "boons.html",
            boon=boon,
            boon_names=[b.name for b in boons.values()],
        )
    except KeyError:
        return render_template("boon-not-found.html", boon=boon_name)


@app.route("/feats")
def feat_index():
    return render_template(
        "feat-index.html", feat_names=[f.name for f in feats.values()]
    )


@app.route("/feats/<feat_name>")
def get_feats(feat_name):
    try:
        feat = feats[feat_name.lower()]
        return render_template(
            "feats.html",
            feat=feat,
            feat_names=[f.name for f in feats.values()],
        )
    except KeyError:
        return render_template("feat-not-found.html", feat=feat_name)


@app.route("/")
def home():
    return render_template("index.html")
