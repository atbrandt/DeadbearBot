from pathlib import Path
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

embedyaml = Path(__file__).parent / "cogs" / "resource" / "embeds.yaml"

embeds = {'embeds': [
            {
            'name': "Shop",
            'head': "**{} Shop**",
            'desc': "Your balance: {} {}\n\n*Buy somethin, will ya!*",
            'fields': [
                {
                'fname': "Custom Role",
                'fdesc': "Buy a custom role! You'll be able to pick both the name and the color of the role after purchase.",
                'inline': True,
                'prompt': "Custom role purchased! Please enter a name for your new role.",
                'limit': 40,
                'format': "text",
                'prompt2': "Next, select a color for your role. You may enter a name from the example image below, or a hex code for a specific custom color, e.g. `0F0F0F`",
                'data': "role",
                'price': 10000,
                'available': 0},
                {
                'fname': "Custom Emoji",
                'fdesc': "Buy a custom emoji! You'll be able to pick both the image and name for the emoji after purchase.",
                'inline': True,
                'prompt': "Custom emoji purchased! Please upload the image you'd like to use for your new emoji.",
                'limit': 10000,
                'format': "image",
                'types': ['.jpeg', '.jpg', '.gif', '.png'],
                'prompt2': "Next, enter the name you want to use for the emoji, with or without `::` around it.",
                'data': "emoji",
                'price': 10000,
                'available': 0}]},
            {
            'name': "Profile",
            'head': "Level: **{}**",
            'desc': "Member of *{}*",
            'fields': [
                {
                'fname': "Total XP",
                'fdesc': "\U0001F4D6 ",
                'inline': False,
                'data': "xp"},
                {
                'fname': "Total Credits",
                'fdesc': "\U0001F48E ",
                'inline': False,
                'data': "cash"},
                {
                'fname': "Name",
                'fdesc': '',
                'inline': True,
                'data': "name"},
                {
                'fname': "Nickname",
                'fdesc': '',
                'inline': True,
                'data': "nickname"},
                {
                'fname': "Age",
                'fdesc': '',
                'inline': True,
                'data': "birthday"},
                {
                'fname': "Gender",
                'fdesc': '',
                'inline': True,
                'data': "gender"},
                {
                'fname': "Location",
                'fdesc': '',
                'inline': True,
                'data': "location"},
                {
                'fname': "Description",
                'fdesc': '',
                'inline': False,
                'data': "description"},
                {
                'fname': "Likes",
                'fdesc': '',
                'inline': True,
                'data': "likes"},
                {
                'fname': "Dislikes",
                'fdesc': '',
                'inline': True,
                'data': "dislikes"}]},
            {
            'name': "Manager",
            'head': "**Profile Customizer**",
            'desc': "Click the emoji that matches to the option you want to change, then follow the instructions that appear above. Use the arrows to navigate to another page, if available.",
            'fields': [
                {
                'fname': "Name",
                'fdesc': "Your **name**, real or otherwise.",
                'inline': True,
                'prompt': "Submit a name, or send `clear` to reset.",
                'limit': 40,
                'format': "text",
                'data': "name"},
                {
                'fname': "Nickname",
                'fdesc': "The **nickname** you like to be called.",
                'inline': True,
                'prompt': "Submit a nickname, or send `clear` to reset.",
                'limit': 60,
                'format': "text",
                'data': "nickname"},
                {
                'fname': "Age",
                'fdesc': "Your **age**, if you want it known.",
                'inline': True,
                'prompt': "Submit a date, using the format `YYYY-MM-DD`, or send `clear` to reset. Note that this date will *not* show up on your profile, it's only used to calculate age!",
                'limit': 10,
                'format': "date",
                'data': "birthday"},
                {
                'fname': "Gender",
                'fdesc': "Your **gender**, whatever it may be.",
                'inline': True,
                'prompt': "Submit a gender, or send `clear` to reset.",
                'limit': 60,
                'format': "text",
                'data': "gender"},
                {
                'fname': "Location",
                'fdesc': "Your **location**, if you want it known.",
                'inline': True,
                'prompt': "Submit a location, or send `clear` to reset.",
                'limit': 80,
                'format': "text",
                'data': "location"},
                {
                'fname': "Description",
                'fdesc': "Your **description**, for general info.",
                'inline': True,
                'prompt': "Submit a description, or send `clear` to reset.",
                'limit': 1024,
                'format': "text",
                'data': "description"},
                {
                'fname': "Likes",
                'fdesc': "A list of **likes**, loves, and interests.",
                'inline': True,
                'prompt': "Submit a list of things you like, separated by commas, e.g. `one thing, something, this_thing`, or send `clear` to reset.",
                'limit': 1024,
                'format': "list",
                'data': "likes"},
                {
                'fname': "Dislikes",
                'fdesc': "A list of **dislikes**, despises, and disinterests.",
                'inline': True,
                'prompt': "Submit a list of things you don't like, separated by commas, e.g. `one thing, something, this_thing`, or send `clear` to reset.",
                'limit': 1024,
                'format': "list",
                'data': "dislikes"}]}]}


if not embedyaml.is_file():
    with open(embedyaml, 'w') as stream:
        dump(embeds, stream, Dumper=Dumper, sort_keys=False, indent=4)
