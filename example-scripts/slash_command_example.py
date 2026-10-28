@nightyScript(
    name="Slash Command Example",
    author="rico",
    description="Typed slash commands, groups, and autocomplete",
    usage="Native slash commands"
)
def slash_command_example():
    """
    SLASH COMMAND EXAMPLE

    SETUP:
    1. Copy the framework block from lord-m1nx/nighty-slash-api.
    2. Paste it at the marked line inside this function.
    3. Keep the SlashAPI label unique across enabled scripts.

    COMMANDS:
    /account id - Show the invoking account ID
    /account context - Show the current Discord context
    /tools echo - Repeat text
    /color - Choose a color with autocomplete
    """
    from typing import Literal

    # Paste the SLASH API START / END block here.

    slash = SlashAPI(label="DocsSlashExample")

    account = slash.group("account", "Account details")

    @account.command(name="id", description="Show your Discord account ID")
    async def account_id(ctx):
        await ctx.send(f"Your account ID is `{ctx.user.id}`.", ephemeral=True)

    @account.command(name="context", description="Show where this command is running")
    async def account_context(ctx):
        guild = ctx.guild or ctx.selfbot_guild
        if guild:
            await ctx.send(
                f"Server: **{guild.name}**\nServer ID: `{guild.id}`",
                ephemeral=True
            )
        else:
            await ctx.send("Context: direct message or group chat", ephemeral=True)

    tools = slash.group("tools", "Text tools")

    @tools.command(
        name="echo",
        description="Repeat text",
        describe={
            "text": "Text to repeat",
            "visibility": "Choose who can see the response"
        }
    )
    async def tools_echo(
        ctx,
        text: str,
        visibility: Literal["private", "public"] = "private"
    ):
        await ctx.send(text[:1900], ephemeral=visibility == "private")

    colors = ["blue", "green", "orange", "red", "violet"]

    @slash.command(description="Choose a saved color")
    async def color(ctx, name: str):
        await ctx.send(f"Selected **{name}**.", ephemeral=True)

    @color.autocomplete("name")
    async def color_autocomplete(ctx, current: str):
        query = current.casefold()
        return [name for name in colors if query in name.casefold()][:25]

    @slash.menu("Show Message ID", target="message")
    async def show_message_id(ctx, message: discord.Message):
        await ctx.send(f"`{message.id}`", ephemeral=True)

    @slash.error
    async def slash_error(ctx, error):
        print(f"[Slash Command Example] {error}", type_="ERROR")
        await ctx.error("The command failed. Check the Nighty console.")

    slash.autosync()


slash_command_example()
