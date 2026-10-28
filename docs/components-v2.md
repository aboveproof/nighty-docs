# Discord Components V2

Components V2 builds a message from layout components instead of a standard embed. Nighty scripts can send V2 payloads from slash interactions through Discord's interaction callback API.

This guide documents the pattern used by VC Manager and nes's Nighty V2 theme schema.

## Message flags

```python
COMPONENTS_V2_FLAG = 1 << 15
EPHEMERAL_FLAG = 1 << 6
```

Set the Components V2 flag on the first interaction response. Add the ephemeral flag when the response should remain visible to the command user.

Components V2 messages place visible text inside the `components` array. Do not send a standard `content` or `embeds` field with the same V2 message.

## Component types used by Nighty themes

| Type | Name | Purpose |
|---:|---|---|
| 9 | Section | Text with an accessory such as a thumbnail |
| 10 | Text display | Markdown text |
| 11 | Thumbnail | Section accessory image |
| 12 | Media gallery | One or more images |
| 14 | Separator | Divider and spacing |
| 17 | Container | Accent color and child layout |

Discord limits component counts and text lengths. Keep a container below 40 child components and keep each text display below 4,000 characters.

## Minimal payload

```python
payload = {
    "type": 4,
    "data": {
        "flags": (1 << 15) | (1 << 6),
        "components": [
            {
                "type": 17,
                "accent_color": 0x5865F2,
                "components": [
                    {"type": 10, "content": "## Build complete\n12 checks passed."}
                ]
            }
        ],
        "allowed_mentions": {"parse": []}
    }
}
```

`allowed_mentions` prevents user-controlled text from creating mentions.

## Nighty V2 theme schema

nes's theme builder stores this shape in the active theme file:

```json
{
  "v2": {
    "enabled": true,
    "color": "#5865F2",
    "layout": [
      {"text": "## Status"},
      {"separator": "small"},
      {
        "section": {
          "text": "{content}",
          "thumbnail": "https://example.com/icon.png"
        }
      },
      {"image": "https://example.com/banner.png"}
    ]
  }
}
```

`{content}` marks the insertion point for the command response. Add the response at the start when the layout has no insertion marker.

## Theme layout builder

```python
def build_v2_layout(content):
    def trim_text(value):
        value = str(value or "")
        return value if len(value) <= 3900 else value[:3897] + "..."

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
        accent_color = int(str(v2.get("color", "#5865F2")).lstrip("#"), 16)
    except (TypeError, ValueError):
        accent_color = 0x5865F2

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
            thumbnail = str(section.get("thumbnail") or "").strip()
            inserted = inserted or "{content}" in text
            rendered = trim_text(text.replace("{content}", content))

            if thumbnail.startswith(("https://", "http://")):
                children.append({
                    "type": 9,
                    "components": [{"type": 10, "content": rendered}],
                    "accessory": {
                        "type": 11,
                        "media": {"url": thumbnail}
                    }
                })
            else:
                children.append({"type": 10, "content": rendered})

        elif "image" in item:
            image_url = str(item.get("image") or "").strip()
            if image_url.startswith(("https://", "http://")):
                children.append({
                    "type": 12,
                    "items": [{"media": {"url": image_url}}]
                })

        elif "separator" in item:
            spacing = 2 if str(item.get("separator")).lower() == "large" else 1
            children.append({"type": 14, "divider": True, "spacing": spacing})

    if not inserted:
        children.insert(0, {"type": 10, "content": content})

    if not children:
        children = [{"type": 10, "content": content}]

    return [{
        "type": 17,
        "accent_color": accent_color,
        "components": children[:39]
    }]
```

## Send an interaction response

Nighty bundles `aiohttp` in current builds. Document it as a dependency in scripts that use this helper.

```python
import aiohttp

async def send_v2(interaction, title, description, ephemeral=True):
    content = f"## {title}\n{description}" if title else description
    interaction_id = str(getattr(interaction, "id", "") or "")
    interaction_token = str(getattr(interaction, "token", "") or "")
    if not interaction_id or not interaction_token:
        return False

    flags = COMPONENTS_V2_FLAG | (EPHEMERAL_FLAG if ephemeral else 0)
    payload = {
        "type": 4,
        "data": {
            "flags": flags,
            "components": build_v2_layout(content),
            "allowed_mentions": {"parse": []}
        }
    }

    url = (
        "https://discord.com/api/v10/interactions/"
        f"{interaction_id}/{interaction_token}/callback"
    )
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status in (200, 204):
                    return True
                detail = (await response.text())[:300]
                print(
                    f"[Components V2] Discord returned {response.status}: {detail}",
                    type_="ERROR"
                )
    except Exception as error:
        print(f"[Components V2] Send error: {error}", type_="ERROR")
    return False
```

Call the helper before the interaction receives another response:

```python
@slash.command(description="Show a Components V2 status card")
async def status(ctx):
    sent = await send_v2(
        ctx.interaction,
        "Service status",
        "**Gateway:** Connected\n**Latency:** 42 ms",
        ephemeral=True
    )
    if not sent:
        await ctx.send("Gateway: connected\nLatency: 42 ms", ephemeral=True)
```

## Edit the original response

```python
async def edit_v2(interaction, title, description):
    content = f"## {title}\n{description}" if title else description
    application_id = getattr(interaction, "application_id", None)
    interaction_token = str(getattr(interaction, "token", "") or "")
    if not application_id or not interaction_token:
        return False

    url = (
        f"https://discord.com/api/v10/webhooks/{application_id}/"
        f"{interaction_token}/messages/@original?with_components=true"
    )
    payload = {
        "components": build_v2_layout(content),
        "allowed_mentions": {"parse": []}
    }

    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.patch(url, json=payload) as response:
                return response.status == 200
    except Exception as error:
        print(f"[Components V2] Edit error: {error}", type_="ERROR")
        return False
```

Interaction tokens expire. Edit the original response while the token remains valid.

## Response fallback

A V2 helper should return a result instead of hiding failures. The caller can send plain text through the Slash API when Discord rejects the raw payload.

```python
if not await send_v2(ctx.interaction, "Report", report_text):
    await ctx.send(report_text[:2000], ephemeral=True)
```

Do not attempt a fallback after Discord accepted the raw callback. Discord permits one initial response.

## Security

- Keep interaction tokens out of logs.
- Set `allowed_mentions` for user-controlled text.
- Accept media URLs from trusted sources or validate their scheme.
- Limit text before building the payload.
- Use a request timeout.

## Common errors

### HTTP 400

Inspect the response body in the Nighty console. Check component types, nesting, field names, text limits, and the Components V2 flag.

### Interaction already acknowledged

The script sent a response before the V2 callback. Send V2 first or edit the existing response.

### Theme does not apply

Check the selected Nighty theme file for an enabled `v2` object. The fallback layout uses the theme color and a text display.

### Image does not render

Discord must fetch the URL. Use an HTTP or HTTPS URL that does not require cookies or request headers.

## Example

See [`components_v2_example.py`](../example-scripts/components_v2_example.py).
