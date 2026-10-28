@nightyScript(
    name="Components V2 Example",
    author="rico",
    description="Send a themed Components V2 slash response",
    usage="/v2status"
)
def components_v2_example():
    """
    COMPONENTS V2 EXAMPLE

    DEPENDENCIES:
    - aiohttp, bundled with current Nighty builds
    - lord-m1nx/nighty-slash-api framework block

    SETUP:
    Paste the Slash API framework block at the marked line inside this function.

    COMMANDS:
    /v2status - Send a private Components V2 status card
    """
    import aiohttp

    # Paste the SLASH API START / END block here.

    COMPONENTS_V2_FLAG = 1 << 15
    EPHEMERAL_FLAG = 1 << 6

    def trim_text(value):
        value = str(value or "")
        return value if len(value) <= 3900 else value[:3897] + "..."

    def build_layout(content):
        content = trim_text(content)
        try:
            theme_name = getConfigData().get("theme")
            theme_data = getThemeData(theme_name=theme_name) or {}
        except Exception:
            theme_data = {}

        v2 = theme_data.get("v2") if isinstance(theme_data, dict) else None
        if not isinstance(v2, dict) or not v2.get("enabled", False):
            v2 = {
                "color": theme_data.get("color", "#5865F2"),
                "layout": [{"text": "{content}"}]
            }

        try:
            accent = int(str(v2.get("color", "#5865F2")).lstrip("#"), 16)
        except (TypeError, ValueError):
            accent = 0x5865F2

        children = []
        inserted = False

        for item in v2.get("layout", []):
            if not isinstance(item, dict):
                continue

            if "text" in item:
                text = str(item.get("text") or "")
                inserted = inserted or "{content}" in text
                children.append({
                    "type": 10,
                    "content": trim_text(text.replace("{content}", content))
                })

            elif isinstance(item.get("section"), dict):
                section = item["section"]
                text = str(section.get("text") or "")
                image = str(section.get("thumbnail") or "").strip()
                inserted = inserted or "{content}" in text
                rendered = trim_text(text.replace("{content}", content))
                if image.startswith(("https://", "http://")):
                    children.append({
                        "type": 9,
                        "components": [{"type": 10, "content": rendered}],
                        "accessory": {"type": 11, "media": {"url": image}}
                    })
                else:
                    children.append({"type": 10, "content": rendered})

            elif "image" in item:
                image = str(item.get("image") or "").strip()
                if image.startswith(("https://", "http://")):
                    children.append({
                        "type": 12,
                        "items": [{"media": {"url": image}}]
                    })

            elif "separator" in item:
                spacing = 2 if str(item.get("separator")).lower() == "large" else 1
                children.append({"type": 14, "divider": True, "spacing": spacing})

        if not inserted:
            children.insert(0, {"type": 10, "content": content})

        return [{
            "type": 17,
            "accent_color": accent,
            "components": (children or [{"type": 10, "content": content}])[:39]
        }]

    async def send_v2(interaction, title, description, ephemeral=True):
        interaction_id = str(getattr(interaction, "id", "") or "")
        interaction_token = str(getattr(interaction, "token", "") or "")
        if not interaction_id or not interaction_token:
            return False

        content = f"## {title}\n{description}" if title else description
        flags = COMPONENTS_V2_FLAG | (EPHEMERAL_FLAG if ephemeral else 0)
        payload = {
            "type": 4,
            "data": {
                "flags": flags,
                "components": build_layout(content),
                "allowed_mentions": {"parse": []}
            }
        }
        url = (
            "https://discord.com/api/v10/interactions/"
            f"{interaction_id}/{interaction_token}/callback"
        )

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status in (200, 204):
                        return True
                    detail = (await response.text())[:300]
                    print(
                        f"[Components V2 Example] Discord returned "
                        f"{response.status}: {detail}",
                        type_="ERROR"
                    )
        except Exception as error:
            print(f"[Components V2 Example] Send error: {error}", type_="ERROR")
        return False

    slash = SlashAPI(label="DocsComponentsV2Example")

    @slash.command(description="Show a Components V2 status card")
    async def v2status(ctx):
        sent = await send_v2(
            ctx.interaction,
            "Nighty status",
            "**Gateway:** Connected\n**Scripts:** Ready",
            ephemeral=True
        )
        if not sent:
            await ctx.send("Gateway: connected\nScripts: ready", ephemeral=True)

    slash.autosync()


components_v2_example()
