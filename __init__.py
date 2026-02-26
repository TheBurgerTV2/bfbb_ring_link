import itertools
import os
import typing
from typing import TextIO

import settings
from BaseClasses import Item, Tutorial, ItemClassification
from Options import Accessibility
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import Component, components, Type, SuffixIdentifier, icon_paths
from .Events import create_events
from .Items import item_table, BfBBItem
from .Locations import location_table, BfBBLocation, patrick_location_table
from .Options import BfBBOptions, RandomizeGateCost
from .Regions import create_regions
from .Rom import BfBBContainer
from .Rules import set_rules
from .Settings import BattleForBikiniBottomSettings
from .Tracker import tracker_world_overview, tracker_world_detailed
from .constants import ItemNames, ConnectionNames, game_name


def run_client(*args):
    print('running bfbb client', args)
    from worlds.LauncherComponents import launch
    from worlds.bfbb.BfBBClient import launch as bfbb_launch  # lazy import
    launch(bfbb_launch, f"{game_name} Client", args=args)

icon_paths["bfbb_icon"] = f"ap:{__name__}/icon.png"
components.append(Component(f"{game_name} Client", func=run_client, component_type=Type.CLIENT,
                            file_identifier=SuffixIdentifier('.apbfbb'), game_name=game_name, supports_uri=True, icon="bfbb_icon"))


class BattleForBikiniBottomWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the SpongeBob SquarePants: Battle for Bikini Bottom integration for Archipelago multiworld games.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Cyb3R"]
    )]
    rich_text_options_doc = True
    theme = "ocean"


default_gate_costs: typing.Dict[str, int] = {
    # ConnectionNames.pineapple_hub1: 1,
    ConnectionNames.hub1_bb01: 5,
    ConnectionNames.hub1_gl01: 10,
    ConnectionNames.hub1_b1: 15,
    ConnectionNames.hub2_rb01: 25,
    ConnectionNames.hub2_sm01: 30,
    ConnectionNames.hub2_b2: 40,
    ConnectionNames.hub3_kf01: 50,
    ConnectionNames.hub3_gy01: 60,
    ConnectionNames.cb_b3: 75,
}


class BattleForBikiniBottom(World):
    """
    SpongeBob SquarePants: Battle for Bikini Bottom
    ToDo
    """
    game = game_name
    options_dataclass = BfBBOptions
    options: BfBBOptions
    settings: typing.ClassVar[BattleForBikiniBottomSettings]
    settings_key = "bfbb_options"
    topology_present = False

    item_name_to_id = {name: data.id for name, data in item_table.items()}
    location_name_to_id = location_table
    location_name_groups = {
      "Hub": {
      "Hub1: On Top of the Pineapple",
      "Hub1: Lost Sock (Patrick)",
      "Hub1: Golden Underwear #1",
      "Hub2: On Top of Shady Shoals",
      "Hub2: Lost Sock (Fountain)",
      "Hub2: Golden Underwear #2",
      "Hub3: On Top of the Chum Bucket",
      "Hub3: Lost Sock (Behind KK under trash)",
      "Hub3: Golden Underwear #3",
      "Pineapple: SpongeBob's Closet",
      "Pineapple: Lost Sock (Library)",
      "Squidward: Annoy Squidward",
      "Squidward: Lost Sock (Destroy furniture)",
      "Tree Dome: Ambush at the Tree Dome",
      "Shoals: Lost Sock (Shoals)",
      "Krusty Krab: Infestation at the Krusty Krab",
      "Krusty Krab: Lost Sock (Destroy furniture)",
      "Chum Bucket: A Wall Jump in the Bucket",
      "Hub3: On Top of the Chum Bucket"
      },
      "Bosses": {
      "JF04: King Jellyfish Jelly",
      "Poseidome: Bubble Bowl",
      "Poseidome: Defeat Robo-Sandy",
      "Merm05: Defeat Prawn",
      "IP: Cruise Bubble",
      "IP: Defeat Robo-Patrick",
      "GY04: Defeat the Flying Dutchman",
      "CB Lab: KAH - RAH - TAE!",
      "CB Lab: The Small Shall Rule... Or No"
      },
      "Mr. Krabs": {
      "Hub: Pay Mr. Krabs 3000 Shiny Objects",
      "Hub: Pay Mr. Krabs 3500 Shiny Objects",
      "Hub: Pay Mr. Krabs 4000 Shiny Objects",
      "Hub: Pay Mr. Krabs 4500 Shiny Objects",
      "Hub: Pay Mr. Krabs 5000 Shiny Objects",
      "Hub: Pay Mr. Krabs 5500 Shiny Objects",
      "Hub: Pay Mr. Krabs 6500 Shiny Objects",
      "Hub: Pay Mr. Krabs 7500 Shiny Objects"
      },
      "Patrick": {
      "Hub1: Return 10 Socks To Patrick",
      "Hub1: Return 20 Socks To Patrick",
      "Hub1: Return 30 Socks To Patrick",
      "Hub1: Return 40 Socks To Patrick",
      "Hub1: Return 50 Socks To Patrick",
      "Hub1: Return 60 Socks To Patrick",
      "Hub1: Return 70 Socks To Patrick",
      "Hub1: Return 80 Socks To Patrick"
      },
      "Downtown Bikini Bottom": {
      "BB01: End of the Road",
      "BB01: Learn Sandy's Moves",
      "BB01: Lost Sock #1 (On broken house)",
      "BB01: Lost Sock #2 (In broken house)",
      "BB01: Lost Sock #3 (On floating platform)",
      "BB01: Lost Sock #4 (On copper house)",
      "BB01: Purple Shiny Object #1 (At fenced off glove near lighthouse)",
      "BB01: Purple Shiny Object #2 (On platform near lighthouse)",
      "BB01: Steering Wheel #1 (On tikis near start)",
      "BB01: Steering Wheel #2 (On canopy)",
      "BB01: Steering Wheel #3 (On house with cannon near rooftops exit)",
      "BB01: Steering Wheel #4 (On crashed boat near sea needle)",
      "BB01: Steering Wheel #5 (Above G-Love near hole)",
      "BB01: Tikis Go Boom",
      "BB02: Across the Rooftops",
      "BB02: Lost Sock #1 (On windmill)",
      "BB02: Lost Sock #2 (Under slide)",
      "BB02: Lost Sock #3 (Behind lighthouse)",
      "BB02: Purple Shiny Object #1 (On floating platforms)",
      "BB02: Purple Shiny Object #2 (On top of windmill blades)",
      "BB02: Steering Wheel #6 (On pipe near start)",
      "BB02: Steering Wheel #7 (Under slide)",
      "BB02: Steering Wheel #8 (On floating platforms)",
      "BB02: Swingin' Sandy",
      "BB03: Ambush in the Lighthouse",
      "BB03: Lost Sock (On top)",
      "BB03: Purple Shiny Object (In tiki stack)",
      "BB03: Steering Wheel #9 (At bottom)",
      "BB04: Come Back With the Cruise Bubble",
      "BB04: Extreme Bungee",
      "BB04: Lost Sock (South side)",
      "BB04: Purple Shiny Object (South side)",
      "BB04: Steering Wheel #10 (East side)",
      "BB04: Steering Wheel #11 (North side)"
      },
      "BB01": {
      "BB01: End of the Road",
      "BB01: Learn Sandy's Moves",
      "BB01: Lost Sock #1 (On broken house)",
      "BB01: Lost Sock #2 (In broken house)",
      "BB01: Lost Sock #3 (On floating platform)",
      "BB01: Lost Sock #4 (On copper house)",
      "BB01: Purple Shiny Object #1 (At fenced off glove near lighthouse)",
      "BB01: Purple Shiny Object #2 (On platform near lighthouse)",
      "BB01: Steering Wheel #1 (On tikis near start)",
      "BB01: Steering Wheel #2 (On canopy)",
      "BB01: Steering Wheel #3 (On house with cannon near rooftops exit)",
      "BB01: Steering Wheel #4 (On crashed boat near sea needle)",
      "BB01: Steering Wheel #5 (Above G-Love near hole)",
      "BB01: Tikis Go Boom"
      },
      "BB02": {
      "BB02: Across the Rooftops",
      "BB02: Lost Sock #1 (On windmill)",
      "BB02: Lost Sock #2 (Under slide)",
      "BB02: Lost Sock #3 (Behind lighthouse)",
      "BB02: Purple Shiny Object #1 (On floating platforms)",
      "BB02: Purple Shiny Object #2 (On top of windmill blades)",
      "BB02: Steering Wheel #6 (On pipe near start)",
      "BB02: Steering Wheel #7 (Under slide)",
      "BB02: Steering Wheel #8 (On floating platforms)",
      "BB02: Swingin' Sandy"
      },
      "BB03": {
      "BB03: Ambush in the Lighthouse",
      "BB03: Lost Sock (On top)",
      "BB03: Purple Shiny Object (In tiki stack)",
      "BB03: Steering Wheel #9 (At bottom)",
      },
      "BB04": {
      "BB04: Come Back With the Cruise Bubble",
      "BB04: Extreme Bungee",
      "BB04: Lost Sock (South side)",
      "BB04: Purple Shiny Object (South side)",
      "BB04: Steering Wheel #10 (East side)",
      "BB04: Steering Wheel #11 (North side)"
      },
      "Kelp Forest": {
      "KF01: Find All the Lost Campers",
      "KF01: Lost Camper #1 (Near Ms Puff)",
      "KF01: Lost Camper #2 (Near waterfall)",
      "KF01: Lost Camper #3 (Near slide area exit)",
      "KF01: Lost Sock #1 (On high platform near Ms. Puff)",
      "KF01: Lost Sock #2 (At waterfall)",
      "KF01: Lost Sock #3 (Tiki bowling)",
      "KF01: Purple Shiny Object (Near waterfall)",
      "KF01: Through the Woods",
      "KF02: Down in the Swamp",
      "KF02: Lost Camper #4",
      "KF02: Lost Camper #5 (At gate)",
      "KF02: Lost Sock #1 (On ledge)",
      "KF02: Lost Sock #2 (On tiki stack)",
      "KF02: Purple Shiny Object (Bungee near waterfall)",
      "KF02: Tiki Roundup",
      "KF04: Lost Camper #6 (Near exit)",
      "KF04: Lost Sock (On ledge near entrance)",
      "KF04: Power Crystal #1 (behind 1st gate)",
      "KF04: Power Crystal #2 (water room top)",
      "KF04: Power Crystal #3 (top near 3rd gate)",
      "KF04: Power Crystal #4 (top big room)",
      "KF04: Power Crystal #5 (top tall vine room)",
      "KF04: Power Crystal #6 (top last room)",
      "KF04: Power Crystal Crisis",
      "KF04: Purple Shiny Object (Top of tall room)",
      "KF04: Through the Kelp Caves",
      "KF05: Beat Mermaid Man's Time",
      "KF05: Kelp Vine Slide",
      "KF05: Lost Sock (On slide)",
      "KF05: Purple Shiny Object (On slide)"
      },
      "KF01": {
      "KF01: Find All the Lost Campers",
      "KF01: Lost Camper #1 (Near Ms Puff)",
      "KF01: Lost Camper #2 (Near waterfall)",
      "KF01: Lost Camper #3 (Near slide area exit)",
      "KF01: Lost Sock #1 (On high platform near Ms. Puff)",
      "KF01: Lost Sock #2 (At waterfall)",
      "KF01: Lost Sock #3 (Tiki bowling)",
      "KF01: Purple Shiny Object (Near waterfall)",
      "KF01: Through the Woods"
      },
      "KF02": {
      "KF02: Down in the Swamp",
      "KF02: Lost Camper #4",
      "KF02: Lost Camper #5 (At gate)",
      "KF02: Lost Sock #1 (On ledge)",
      "KF02: Lost Sock #2 (On tiki stack)",
      "KF02: Purple Shiny Object (Bungee near waterfall)",
      "KF02: Tiki Roundup"
      },
      "KF04": {
      "KF04: Lost Camper #6 (Near exit)",
      "KF04: Lost Sock (On ledge near entrance)",
      "KF04: Power Crystal #1 (behind 1st gate)",
      "KF04: Power Crystal #2 (water room top)",
      "KF04: Power Crystal #3 (top near 3rd gate)",
      "KF04: Power Crystal #4 (top big room)",
      "KF04: Power Crystal #5 (top tall vine room)",
      "KF04: Power Crystal #6 (top last room)",
      "KF04: Power Crystal Crisis",
      "KF04: Purple Shiny Object (Top of tall room)",
      "KF04: Through the Kelp Caves"
      },
      "KF05": {
      "KF05: Beat Mermaid Man's Time",
      "KF05: Kelp Vine Slide",
      "KF05: Lost Sock (On slide)",
      "KF05: Purple Shiny Object (On slide)"
      },
      "Jellyfish Fields": {
      "JF01: Cowa-Bungee!",
      "JF01: Defeat King Jellyfish",
      "JF01: Lost Sock #1 (On JF rock)",
      "JF01: Lost Sock #2 (Bungee)",
      "JF01: Lost Sock #3 (On island)",
      "JF01: Lost Sock #4 (Fountain)",
      "JF01: Lost Sock #5 (On goo)",
      "JF01: Lost Sock #6 (Bowling minigame)",
      "JF01: Purple Shiny Object (On island)",
      "JF01: Top of the Hill",
      "JF02: Lost Sock #1 (On slide)",
      "JF02: Lost Sock #2 (After slide)",
      "JF02: Lost Sock #3 (In cave near slide)",
      "JF02: Lost Sock #4 (On goo in cave)",
      "JF02: Patrick's Dilemma",
      "JF02: Purple Shiny Object (On goo near exit)",
      "JF02: Spelunking",
      "JF03: Drain the Lake",
      "JF03: Lost Sock #1 (On Cliff near Clamp)",
      "JF03: Lost Sock #2 (Tiki Minigame)",
      "JF03: Lost Sock #3 (Near wall jumps)",
      "JF03: Navigate the Canyons and Mesas",
      "JF03: Purple Shiny Object (On goo under bridge)",
      "JF04: King Jellyfish Jelly",
      "JF04: Lost Sock (On Slide after King JF)",
      "JF04: Purple Shiny Object (On slide)",
      "JF04: Slide Leap"
      },
      "JF01": {
      "JF01: Cowa-Bungee!",
      "JF01: Defeat King Jellyfish",
      "JF01: Lost Sock #1 (On JF rock)",
      "JF01: Lost Sock #2 (Bungee)",
      "JF01: Lost Sock #3 (On island)",
      "JF01: Lost Sock #4 (Fountain)",
      "JF01: Lost Sock #5 (On goo)",
      "JF01: Lost Sock #6 (Bowling minigame)",
      "JF01: Purple Shiny Object (On island)",
      "JF01: Top of the Hill"
      },
      "JF02": {
      "JF02: Lost Sock #1 (On slide)",
      "JF02: Lost Sock #2 (After slide)",
      "JF02: Lost Sock #3 (In cave near slide)",
      "JF02: Lost Sock #4 (On goo in cave)",
      "JF02: Patrick's Dilemma",
      "JF02: Purple Shiny Object (On goo near exit)",
      "JF02: Spelunking"
      },
      "JF03": {
      "JF03: Drain the Lake",
      "JF03: Lost Sock #1 (On Cliff near Clamp)",
      "JF03: Lost Sock #2 (Tiki Minigame)",
      "JF03: Lost Sock #3 (Near wall jumps)",
      "JF03: Navigate the Canyons and Mesas",
      "JF03: Purple Shiny Object (On goo under bridge)"
      },
      "JF04": {
      "JF04: King Jellyfish Jelly",
      "JF04: Lost Sock (On Slide after King JF)",
      "JF04: Purple Shiny Object (On slide)",
      "JF04: Slide Leap"
      },
      "Goo Lagoon": {
      "GL01: Balloon Kid #1 (Near Ms. Puff)",
      "GL01: Balloon Kid #2 (On beach near moving logs)",
      "GL01: Balloon Kid #3 (On beach near sinking logs)",
      "GL01: Balloon Kid #4 (On Water near moving logs)",
      "GL01: Balloon Kid #5 (On Water near sinking logs)",
      "GL01: Connect the Towers",
      "GL01: King of the Castle",
      "GL01: Lost Sock #1 (On watchtower)",
      "GL01: Lost Sock #2 (In sand castle)",
      "GL01: Lost Sock #3 (On juice bar)",
      "GL01: Lost Sock #4 (On top of sand castle)",
      "GL01: Lost Sock #5 (Sand castle entrance gate)",
      "GL01: Over the Moat",
      "GL01: Purple Shiny Object (End of log path near Ms. Puff)",
      "GL01: Save the Children",
      "GL02: Lost Sock #1 (Under ledge near entrance)",
      "GL02: Lost Sock #2 (On goo)",
      "GL02: Lost Sock #3 (On side ledge)",
      "GL02: Purple Shiny Object (On ledge under checkpoint)",
      "GL02: Through the Sea Caves",
      "GL03: Clean out the Bumper Boats",
      "GL03: Lost Sock #1 (Tiki minigame)",
      "GL03: Lost Sock #2 (Sliding minigame)",
      "GL03: Lost Sock #3 (On booth)",
      "GL03: Purple Shiny Object (On tikis after slide)",
      "GL03: Slip and Slide Under the Pier",
      "GL03: Tower Bungee"
      },
      "GL01": {
      "GL01: Balloon Kid #1 (Near Ms. Puff)",
      "GL01: Balloon Kid #2 (On beach near moving logs)",
      "GL01: Balloon Kid #3 (On beach near sinking logs)",
      "GL01: Balloon Kid #4 (On Water near moving logs)",
      "GL01: Balloon Kid #5 (On Water near sinking logs)",
      "GL01: Connect the Towers",
      "GL01: King of the Castle",
      "GL01: Lost Sock #1 (On watchtower)",
      "GL01: Lost Sock #2 (In sand castle)",
      "GL01: Lost Sock #3 (On juice bar)",
      "GL01: Lost Sock #4 (On top of sand castle)",
      "GL01: Lost Sock #5 (Sand castle entrance gate)",
      "GL01: Over the Moat",
      "GL01: Purple Shiny Object (End of log path near Ms. Puff)",
      "GL01: Save the Children"
      },
      "GL02": {
      "GL02: Lost Sock #1 (Under ledge near entrance)",
      "GL02: Lost Sock #2 (On goo)",
      "GL02: Lost Sock #3 (On side ledge)",
      "GL02: Purple Shiny Object (On ledge under checkpoint)",
      "GL02: Through the Sea Caves"
      },
      "GL03": {
      "GL03: Clean out the Bumper Boats",
      "GL03: Lost Sock #1 (Tiki minigame)",
      "GL03: Lost Sock #2 (Sliding minigame)",
      "GL03: Lost Sock #3 (On booth)",
      "GL03: Purple Shiny Object (On tikis after slide)",
      "GL03: Slip and Slide Under the Pier",
      "GL03: Tower Bungee"
      },
      "Mermalair": {
      "Merm01: Lost Sock (Bungee)",
      "Merm01: Purple Shiny Object (Duplicatotron bowling)",
      "Merm01: Top of the Entrance Area",
      "Merm02: Lost Sock (On light)",
      "Merm02: Purple Shiny Object #1 (In hidden cave near entrance)",
      "Merm02: Purple Shiny Object #2 (On slide)",
      "Merm02: Security Override Button #1 (At Computer)",
      "Merm02: Security Override Button #2 (At Lasers)",
      "Merm02: Shut Down the Security System",
      "Merm02: The Funnel Machines",
      "Merm02: The Spinning Towers of Power",
      "Merm02: Top of the Computer Area",
      "Merm03: Lost Sock (Conveyor clamp)",
      "Merm03: Purple Shiny Object (Above disco floor at 2nd tunnel entrance)",
      "Merm03: Security Override Button #3 (At Top)",
      "Merm03: Top of the Security Tunnel",
      "Merm04: Complete the Rolling Ball Room",
      "Merm04: Lost Sock (Behind tilting platform near end)",
      "Merm04: Purple Shiny Object (In ball dispenser)",
      "Merm04: Security Override Button #4 (Next to ramp)",
      "Merm05: Defeat Prawn"
      },
      "Merm01": {
      "Merm01: Lost Sock (Bungee)",
      "Merm01: Purple Shiny Object (Duplicatotron bowling)",
      "Merm01: Top of the Entrance Area"
      },
      "Merm02": {
      "Merm02: Lost Sock (On light)",
      "Merm02: Purple Shiny Object #1 (In hidden cave near entrance)",
      "Merm02: Purple Shiny Object #2 (On slide)",
      "Merm02: Security Override Button #1 (At Computer)",
      "Merm02: Security Override Button #2 (At Lasers)",
      "Merm02: Shut Down the Security System",
      "Merm02: The Funnel Machines",
      "Merm02: The Spinning Towers of Power",
      "Merm02: Top of the Computer Area"
      "Merm05: Defeat Prawn"
      },
      "Merm03": {
      "Merm03: Lost Sock (Conveyor clamp)",
      "Merm03: Purple Shiny Object (Above disco floor at 2nd tunnel entrance)",
      "Merm03: Security Override Button #3 (At Top)",
      "Merm03: Top of the Security Tunnel"
      },
      "Merm04": {
      "Merm04: Complete the Rolling Ball Room",
      "Merm04: Lost Sock (Behind tilting platform near end)",
      "Merm04: Purple Shiny Object (In ball dispenser)",
      "Merm04: Security Override Button #4 (Next to ramp)"
      },
      "Rock Bottom": {
      "RB01: Get to the Museum",
      "RB01: Lost Sock #1 (On roof near elevator)",
      "RB01: Lost Sock #2 (On rock)",
      "RB01: Lost Sock #3 (Near slide end)",
      "RB01: Museum Art #1 (On ledge above bubble buddy)",
      "RB01: Museum Art #2 (Near start)",
      "RB01: Purple Shiny Object (Under Swingalong Spatula)",
      "RB01: Return the Museum's Art",
      "RB01: Slip Sliding Away",
      "RB01: Swingalong Spatula",
      "RB02: Lost Sock #1 (Ledge near exit)",
      "RB02: Lost Sock #2 (Midway right ledge)",
      "RB02: Lost Sock #3 (Under entrance)",
      "RB02: Museum Art #3 (Bottom)",
      "RB02: Museum Art #4 (Near exit)",
      "RB02: Plundering Robots in the Museum",
      "RB02: Purple Shiny Object (On roof)",
      "RB03: Across the Trench of Darkness",
      "RB03: How in Tarnation Do You Get There?",
      "RB03: Lasers are Fun and Good for You",
      "RB03: Lost Sock #1 (Bungee)",
      "RB03: Lost Sock #2 (Near Duplicatotron)",
      "RB03: Lost Sock #3 (At button under laser)",
      "RB03: Museum Art #5 (Behind laser)",
      "RB03: Museum Art #6 (On Sleepy-Time platform)",
      "RB03: Purple Shiny Object (By floating tiki near exit)"
      },
      "RB01": {
      "RB01: Get to the Museum",
      "RB01: Lost Sock #1 (On roof near elevator)",
      "RB01: Lost Sock #2 (On rock)",
      "RB01: Lost Sock #3 (Near slide end)",
      "RB01: Museum Art #1 (On ledge above bubble buddy)",
      "RB01: Museum Art #2 (Near start)",
      "RB01: Purple Shiny Object (Under Swingalong Spatula)",
      "RB01: Return the Museum's Art",
      "RB01: Slip Sliding Away",
      "RB01: Swingalong Spatula"
      },
      "RB02": {
      "RB02: Lost Sock #1 (Ledge near exit)",
      "RB02: Lost Sock #2 (Midway right ledge)",
      "RB02: Lost Sock #3 (Under entrance)",
      "RB02: Museum Art #3 (Bottom)",
      "RB02: Museum Art #4 (Near exit)",
      "RB02: Plundering Robots in the Museum",
      "RB02: Purple Shiny Object (On roof)"
      },
      "RB03": {
      "RB03: Across the Trench of Darkness",
      "RB03: How in Tarnation Do You Get There?",
      "RB03: Lasers are Fun and Good for You",
      "RB03: Lost Sock #1 (Bungee)",
      "RB03: Lost Sock #2 (Near Duplicatotron)",
      "RB03: Lost Sock #3 (At button under laser)",
      "RB03: Museum Art #5 (Behind laser)",
      "RB03: Museum Art #6 (On Sleepy-Time platform)",
      "RB03: Purple Shiny Object (By floating tiki near exit)"
      },
      "Sand Mountain": {
      "SM01: Frosty Bungee",
      "SM01: Lost Sock #1 (Below bridge)",
      "SM01: Lost Sock #2 (Snowman)",
      "SM01: Purple Shiny Object (On ledge near entrance)",
      "SM01: Top of the Lodge",
      "SM02: Beat Mrs. Puff's Time",
      "SM02: Defeat Robots on Guppy Mound",
      "SM02: Lost Sock #1 (Ledge near start)",
      "SM02: Lost Sock #2 (Underpass)",
      "SM02: Lost Sock #3 (Ledge near end)",
      "SM02: Purple Shiny Object #1 (On slide under tikis)",
      "SM02: Purple Shiny Object #2 (On stone arch)",
      "SM03: Beat Bubble Buddy's Time",
      "SM03: Defeat Robots on Flounder Hill",
      "SM03: Lost Sock #1 (At end after destroying all Sandmans)",
      "SM03: Lost Sock #2 (On last tunnel near end)",
      "SM03: Sandman #1 (At Start)",
      "SM03: Sandman #2 (Lower path after first turn)",
      "SM03: Sandman #3 (On shortcut)",
      "SM03: Sandman #4 (On right spiral)",
      "SM03: Sandman #5 (On left spiral)",
      "SM03: Sandman #6 (Middle path of 1st 3-way split near end)",
      "SM03: Sandman #7 (Left path of 1st 3-way split near end)",
      "SM03: Sandman #8 (On turn after cave)",
      "SM04: Beat Larry's Time",
      "SM04: Defeat Robots on Sand Mountain",
      "SM04: Lost Sock #1 (Top ledge near start)",
      "SM04: Lost Sock #2 (In hidden cave)",
      "SM04: Lost Sock #3 (On ice platforms)",
      "SM04: Purple Shiny Object (In cave on drop to cave exit)"
      },
      "SM01": {
      "SM01: Frosty Bungee",
      "SM01: Lost Sock #1 (Below bridge)",
      "SM01: Lost Sock #2 (Snowman)",
      "SM01: Purple Shiny Object (On ledge near entrance)",
      "SM01: Top of the Lodge"
      },
      "SM02": {
      "SM02: Beat Mrs. Puff's Time",
      "SM02: Defeat Robots on Guppy Mound",
      "SM02: Lost Sock #1 (Ledge near start)",
      "SM02: Lost Sock #2 (Underpass)",
      "SM02: Lost Sock #3 (Ledge near end)",
      "SM02: Purple Shiny Object #1 (On slide under tikis)",
      "SM02: Purple Shiny Object #2 (On stone arch)"
      },
      "SM03": {
      "SM03: Beat Bubble Buddy's Time",
      "SM03: Defeat Robots on Flounder Hill",
      "SM03: Lost Sock #1 (At end after destroying all Sandmans)",
      "SM03: Lost Sock #2 (On last tunnel near end)",
      "SM03: Sandman #1 (At Start)",
      "SM03: Sandman #2 (Lower path after first turn)",
      "SM03: Sandman #3 (On shortcut)",
      "SM03: Sandman #4 (On right spiral)",
      "SM03: Sandman #5 (On left spiral)",
      "SM03: Sandman #6 (Middle path of 1st 3-way split near end)",
      "SM03: Sandman #7 (Left path of 1st 3-way split near end)",
      "SM03: Sandman #8 (On turn after cave)"
      },
      "SM04": {
      "SM04: Beat Larry's Time",
      "SM04: Defeat Robots on Sand Mountain",
      "SM04: Lost Sock #1 (Top ledge near start)",
      "SM04: Lost Sock #2 (In hidden cave)",
      "SM04: Lost Sock #3 (On ice platforms)",
      "SM04: Purple Shiny Object (In cave on drop to cave exit)"
      },
      "Flying Dutchman's Graveyard": {
      "GY01: A Path Through the Goo",
      "GY01: Goo Tanker Ahoy!",
      "GY01: Lost Sock (On mast platform in goo)",
      "GY01: Purple Shiny Object (On left wall near tubelet)",
      "GY01: Top of the Entrance Area",
      "GY02: Lost Sock (In shipwreck)",
      "GY02: Purple Shiny Object (On mast under 1st ship wall jump section)",
      "GY02: Shipwreck Bungee",
      "GY02: Top of the Stack of Ships",
      "GY03: Destroy the Robot Ship",
      "GY03: Get Aloft There, Matey!",
      "GY03: Lost Sock (On rope on robot ship)",
      "GY03: Purple Shiny Object (On top of mast)",
      "GY03: Ship Cannon #1 (On deck)",
      "GY03: Ship Cannon #2 (On middle mast)",
      "GY03: Ship Cannon #3 (On front mast)",
      "GY03: Ship Cannon #4 (Near steering wheel)",
      "GY04: Defeat the Flying Dutchman"
      },
      "GY01": {
      "GY01: A Path Through the Goo",
      "GY01: Goo Tanker Ahoy!",
      "GY01: Lost Sock (On mast platform in goo)",
      "GY01: Purple Shiny Object (On left wall near tubelet)",
      "GY01: Top of the Entrance Area"
      },
      "GY02": {
      "GY02: Lost Sock (In shipwreck)",
      "GY02: Purple Shiny Object (On mast under 1st ship wall jump section)",
      "GY02: Shipwreck Bungee",
      "GY02: Top of the Stack of Ships"
      },
      "GY03": {
      "GY03: Destroy the Robot Ship",
      "GY03: Get Aloft There, Matey!",
      "GY03: Lost Sock (On rope on robot ship)",
      "GY03: Purple Shiny Object (On top of mast)",
      "GY03: Ship Cannon #1 (On deck)",
      "GY03: Ship Cannon #2 (On middle mast)",
      "GY03: Ship Cannon #3 (On front mast)",
      "GY03: Ship Cannon #4 (Near steering wheel)",
      "GY04: Defeat the Flying Dutchman"
      },
      "Spongebob's Dream": {
      "Dream01: Across the Dreamscape",
      "Dream01: Follow the Bouncing Ball",
      "Dream01: Purple Shiny Object (Behind Krusty Krab)",
      "Dream01: Super Bounce",
      "Dream02: Lost Sock #1 (On top slide near skull)",
      "Dream02: Lost Sock #2 (Oil tower)",
      "Dream02: Lost Sock #3 (Behind house on Swingers platform)",
      "Dream02: Purple Shiny Object #1 (On tikis near start)",
      "Dream02: Purple Shiny Object #2 (In flower)",
      "Dream02: Slidin' Texas Style",
      "Dream02: Swingers Ahoy",
      "Dream03: Lost Sock (In air near trampoline)",
      "Dream03: Music is in the Ear of the Beholder",
      "Dream03: Purple Shiny Object (On clarinet)",
      "Dream04: Krabby Patty Platforms",
      "Dream04: Lost Sock (Behind grill)",
      "Dream04: Purple Shiny Object (On floating tiki near start)",
      "Dream05: Here You Go"
      },
      "Dream01": {
      "Dream01: Across the Dreamscape",
      "Dream01: Follow the Bouncing Ball",
      "Dream01: Purple Shiny Object (Behind Krusty Krab)",
      "Dream01: Super Bounce",
      "Dream05: Here You Go"
      },
      "Dream02": {
      "Dream02: Lost Sock #1 (On top slide near skull)",
      "Dream02: Lost Sock #2 (Oil tower)",
      "Dream02: Lost Sock #3 (Behind house on Swingers platform)",
      "Dream02: Purple Shiny Object #1 (On tikis near start)",
      "Dream02: Purple Shiny Object #2 (In flower)",
      "Dream02: Slidin' Texas Style",
      "Dream02: Swingers Ahoy"
      },
      "Dream03": {
      "Dream03: Lost Sock (In air near trampoline)",
      "Dream03: Music is in the Ear of the Beholder",
      "Dream03: Purple Shiny Object (On clarinet)"
      },
      "Dream04": {
      "Dream04: Krabby Patty Platforms",
      "Dream04: Lost Sock (Behind grill)",
      "Dream04: Purple Shiny Object (On floating tiki near start)"
      },
      "Level Item Rewards": {
      "JF01: Defeat King Jellyfish",
      "BB01: End of the Road",
      "GL01: Save the Children",
      "Merm02: Shut Down the Security System",
      "Merm05: Defeat Prawn",
      "RB01: Return the Museum's Art",
      "SM03: Lost Sock #1 (At end after destroying all Sandmans)",
      "KF01: Find All the Lost Campers",
      "KF04: Power Crystal Crisis",
      "GY03: Destroy the Robot Ship",
      "GY03: Get Aloft There, Matey!",
      "GY03: Purple Shiny Object (On top of mast)",
      "GY04: Defeat the Flying Dutchman",
      }
    }

    web = BattleForBikiniBottomWeb()
    ut_can_gen_without_yaml = True

    def __init__(self, multiworld: "MultiWorld", player: int):
        super().__init__(multiworld, player)
        self.gate_costs: typing.Dict[str, int] = default_gate_costs.copy()
        self.level_order: typing.List[str] = [ConnectionNames.hub1_bb01, ConnectionNames.hub1_gl01, ConnectionNames.hub1_b1,
                                              ConnectionNames.hub2_rb01, ConnectionNames.hub2_sm01, ConnectionNames.hub2_b2,
                                              ConnectionNames.hub3_kf01, ConnectionNames.hub3_gy01, ConnectionNames.cb_b3]
        self.spat_counter: int = 0
        self.sock_counter: int = 0
        self.required_socks: int = 80
        self.required_spats: int = 75
        tracker_variant = settings.get_settings().bfbb_options.tracker_variant or 'detailed'
        BattleForBikiniBottom.tracker_world = tracker_world_overview if tracker_variant == 'overview' else tracker_world_detailed

    def generate_early(self) -> None:
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if self.game in self.multiworld.re_gen_passthrough:
                self.apply_options_from_slot_data(self.multiworld.re_gen_passthrough[self.game])
                return

        if self.options.required_spatulas.value > self.options.available_spatulas.value:
            self.options.required_spatulas.value = self.options.available_spatulas.value
        if self.options.randomize_gate_cost.value > RandomizeGateCost.option_off:
            self.roll_level_order()
            self.set_gate_costs()
        self.gate_costs[ConnectionNames.cb_b3] = self.options.required_spatulas.value
        self.required_socks = self.get_required_socks()
        self.required_spats = max(self.gate_costs.values())

    def get_required_socks(self) -> int:
        socks = 80
        for pat_loc in sorted(patrick_location_table, key=patrick_location_table.get, reverse=True):
            if pat_loc in self.options.exclude_locations:
                socks -= 10
            else:
                break
        return socks

    def roll_level_order(self):
        level_left = [ConnectionNames.hub1_bb01, ConnectionNames.hub1_gl01, ConnectionNames.hub2_rb01,
                      ConnectionNames.hub2_sm01, ConnectionNames.hub3_kf01, ConnectionNames.hub3_gy01]
        counts = [4, 4, 2, 2, 1, 1]
        cnt = len(level_left)
        self.level_order = []
        for i in range(0, cnt):
            choices = [*range(0, len(level_left))]
            weighted_choices = list(itertools.chain.from_iterable([[choice] * count for choice, count in zip(choices, counts)]))
            idx = self.random.choice(weighted_choices)
            level = level_left[idx]
            if level in [ConnectionNames.hub2_rb01, ConnectionNames.hub2_sm01, ConnectionNames.hub3_kf01,
                         ConnectionNames.hub3_gy01] and ConnectionNames.hub1_b1 not in self.level_order:
                self.level_order.append(ConnectionNames.hub1_b1)
            if level in [ConnectionNames.hub3_kf01, ConnectionNames.hub3_gy01] and ConnectionNames.hub2_b2 not in self.level_order:
                self.level_order.append(ConnectionNames.hub2_b2)
            self.level_order.append(level)
            level_left.remove(level)
            counts.remove(counts[idx])

    def set_gate_costs(self):
        last_level = None
        min_incs = [0, 3, 5]
        last_cost = 1
        level_inc_min = min_incs[self.options.randomize_gate_cost.value - 1]
        level_inc_max = 8
        if self.options.include_socks.value:
            level_inc_max += 6
        if self.options.include_level_items.value:
            level_inc_max += 3
        if self.options.include_purple_so.value:
            level_inc_max += 1
        if self.options.randomize_gate_cost.value == 3:
            level_inc_max = round(level_inc_max * 1.35)
        elif self.options.randomize_gate_cost.value == 1:
            level_inc_max = round(level_inc_max * 0.75)
        for v in self.level_order:
            # set max increment after boss to 1/2
            if last_level is not None and last_level in [ConnectionNames.hub1_b1, ConnectionNames.hub2_b2]:
                level_inc_max = 2 if self.options.include_skills else 1
            level_inc_min = min(level_inc_min, level_inc_max)
            cost = min(self.random.randint(level_inc_min, level_inc_max) + last_cost, self.options.required_spatulas.value - 1)
            assert cost > 0, f"{v} gate cost too low"
            self.gate_costs[v] = cost
            last_level = v
            last_cost = cost

    def get_filler_item_name(self) -> str:
        return ItemNames.so_100

    def get_items(self):
        filler_items = [ItemNames.so_100, ItemNames.so_250]
        filler_weights = [1, 2]
        if self.options.include_purple_so.value == 0:
            filler_items += [ItemNames.so_500, ItemNames.so_750, ItemNames.so_1000]
            filler_weights += [5, 3, 2]
        # Generate item pool
        itempool = [ItemNames.spat] * self.options.available_spatulas.value
        if 100 - self.options.available_spatulas.value > 0:
            itempool += self.random.choices(filler_items, weights=filler_weights, k=100 - self.options.available_spatulas.value)
        if self.options.include_socks.value:
            itempool += [ItemNames.sock] * 80
        if self.options.include_skills.value:
            itempool += [ItemNames.bubble_bowl, ItemNames.cruise_bubble]
        if self.options.include_golden_underwear.value:
            itempool += [ItemNames.golden_underwear] * 3
        if self.options.include_level_items.value:
            itempool += [ItemNames.lvl_itm_jf]
            itempool += [ItemNames.lvl_itm_bb] * 11
            itempool += [ItemNames.lvl_itm_gl] * 5
            itempool += [ItemNames.lvl_itm_rb] * 6
            itempool += [ItemNames.lvl_itm_bc] * 4
            itempool += [ItemNames.lvl_itm_sm] * 8
            itempool += [ItemNames.lvl_itm_kf1] * 6
            itempool += [ItemNames.lvl_itm_kf2] * 6
            itempool += [ItemNames.lvl_itm_gy] * 4
        if self.options.include_purple_so.value:
            so_items = [ItemNames.so_100, ItemNames.so_250, ItemNames.so_500, ItemNames.so_750, ItemNames.so_1000]
            so_weights = [1, 2, 5, 3, 2]
            itempool += self.random.choices(so_items, weights=so_weights, k=38)

        # Convert itempool into real items
        itempool = list(map(lambda name: self.create_item(name), itempool))
        return itempool

    def create_items(self):
        self.multiworld.itempool += self.get_items()

    def set_rules(self):
        create_events(self.multiworld, self.player)
        set_rules(self.multiworld, self.options, self.player, self.gate_costs)

    def create_regions(self):
        create_regions(self.multiworld, self.options, self.player)

    def fill_slot_data(self):
        return {
            "version": self.world_version.as_simple_string(), #TODO: add version check/warning to patch/client
            "death_link": self.options.death_link.value,
            "ring_link": self.options.ring_link.value,
            "shiny_object_to_ring_ratio": self.options.shiny_object_to_ring_ratio.value,
            "include_socks": self.options.include_socks.value,
            "include_skills": self.options.include_skills.value,
            "include_golden_underwear": self.options.include_golden_underwear.value,
            "include_level_items": self.options.include_level_items.value,
            "include_purple_so": self.options.include_purple_so.value,
            "gate_costs": self.gate_costs
        }

    @staticmethod
    def interpret_slot_data(slot_data: dict):
        return slot_data

    def apply_options_from_slot_data(self, slot_data: dict):
        for k, v in slot_data.items():
            if k == "gate_costs":
                self.gate_costs = v
                continue
            if hasattr(self.options, k):
                option = getattr(self.options, k)
                if option.value != v:
                    option.value = v

    def create_item(self, name: str, ) -> Item:
        item_data = item_table[name]
        classification = item_data.classification
        if name == ItemNames.spat:
            self.spat_counter += 1
            if self.spat_counter > self.required_spats:
                classification |= ItemClassification.skip_balancing
        if name == ItemNames.sock:
            self.sock_counter += 1
            if self.sock_counter > 40:
                classification |= ItemClassification.skip_balancing
            if self.options.accessibility.value == Accessibility.option_minimal and self.sock_counter > self.required_socks:
                classification = ItemClassification.useful
        if name in [ItemNames.so_500, ItemNames.so_750, ItemNames.so_1000] and self.options.include_purple_so == 0:
            classification = ItemClassification.useful
        item = BfBBItem(name, classification, item_data.id, self.player)

        return item

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        if self.options.randomize_gate_cost.value > 0:
            spoiler_handle.write(f"\n\nGate Costs ({self.multiworld.get_player_name(self.player)}):\n\n")
            for k, v in self.gate_costs.items():
                spoiler_handle.write(f"{k}: {v}\n")

    def generate_output(self, output_directory: str) -> None:
        apbfbb = BfBBContainer(
            path=os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}{BfBBContainer.patch_file_ending}"),
            player=self.player,
            player_name=self.multiworld.get_player_name(self.player),
            data={
                "include_socks": bool(self.options.include_socks.value),
                "include_skills": bool(self.options.include_skills.value),
                "include_golden_underwear": bool(self.options.include_golden_underwear.value),
                "include_level_items": bool(self.options.include_level_items.value),
                "include_purple_so": bool(self.options.include_purple_so.value),
                "seed": self.multiworld.seed_name.encode('utf-8'),
                "randomize_gate_cost": self.options.randomize_gate_cost.value,
                "gate_costs": self.gate_costs,
            }
        )
        apbfbb.write()