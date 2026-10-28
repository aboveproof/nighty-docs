# Troubleshooting

Start with the Nighty console. Record the script name, failed action, exception type, and Discord HTTP status. Remove tokens and interaction URLs before sharing logs.

## Script does not load

Check these items:

- The decorated function has a call at the end of the file.
- The script does not import `discord` or `nighty`.
- Imports required by callbacks live inside the script function.
- Python indentation remains inside the decorated function.
- The Nighty console shows no syntax error.

Run a local syntax check:

```bash
python -m py_compile your_script.py
```

This check catches Python syntax errors. It cannot supply Nighty's injected globals.

## `There is no current event loop in thread`

Nighty called the function from a worker thread. Queue the coroutine on the bot loop:

```python
def run_async(coroutine):
    try:
        return bot.loop.create_task(coroutine)
    except Exception:
        try:
            coroutine.close()
        except Exception:
            pass
        raise
```

Use `asyncio.create_task()` only from a coroutine running on an event-loop thread.

## Prefix command does not run

- Confirm the command decorator sits inside the script function.
- Confirm the script function runs at the end of the file.
- Check for another command with the same name.
- Delete or rename legacy commands during a migration to slash commands.

## Slash command does not appear

- Put `slash.autosync()` after all slash decorators.
- Give the script a unique Slash API label.
- Check the console for Discord HTTP 400 details.
- Refresh Discord after the sync.
- Use a development guild when the API version supports guild-scoped sync.

Global command changes can take longer to reach Discord clients.

## Slash command works in servers but not DMs

The command needs user installation and private contexts. Current Slash API builds request:

```python
allowed_contexts(guilds=True, dms=True, private_channels=True)
allowed_installs(guilds=True, users=True)
```

Check that Nighty's application-command library exposes those decorators. Reinstall the command for the user account after changing install contexts.

Treat `ctx.guild` as optional in DM and user-installed contexts.

## `interaction already acknowledged`

The handler sent two initial responses. Use one of these flows:

```python
await ctx.send("Done", ephemeral=True)
```

```python
await ctx.defer(ephemeral=True)
await ctx.send("Done", ephemeral=True)
```

For raw Components V2, send the raw callback first. Use the webhook edit endpoint for later changes.

## Components V2 returns HTTP 400

Log the response body and check:

- `flags` includes `1 << 15`.
- Visible text sits inside component type 10.
- Sections use type 9 and a valid accessory.
- Containers use type 17.
- Child component and text limits stay within Discord limits.
- The payload does not mix standard content or embeds with V2 layout.

## Components V2 theme does not load

Read the active theme name from `getConfigData().get("theme")`, then call `getThemeData(theme_name=...)`.

Check for:

```json
{
  "v2": {
    "enabled": true,
    "color": "#5865F2",
    "layout": [{"text": "{content}"}]
  }
}
```

Use a plain text-display container when the theme has no enabled V2 layout.

## CUI shows raw `__CUI__` text

The browser runtime did not replace the placeholder.

- Run `evaluate_js(JS_CUI)` after the tab renders.
- Register custom templates with `window.cUIData.updateTemplates(...)`.
- Run the placeholder scan after registration.
- Reinstall CUI after Socket.IO connects.
- Disconnect the previous mutation observer before installing a replacement.

## CUI works after restarting Nighty but fails after page refresh

The browser page lost `window.cUIData` while Python stayed loaded. Add a Socket.IO connect handler that reinstalls CUI and its templates.

Keep the installer idempotent. A refresh can reuse the same Socket.IO session in some embedded browsers.

## CUI callback does not fire

Check four points:

1. `_init_params` includes the callback name.
2. `self.funcs` includes the callback.
3. The HTML uses `${callback_name}`.
4. `callback_store.register(_cui_cb)` runs during tab render.

CUI sends the browser element's value as text. Convert numbers and booleans in Python.

## Card width collapses

A hidden custom element may report no width during CUI measurement.

- Set the card width to `full`.
- Give sibling cards the same flex basis.
- Use `disallow_shrink=True` for narrow content-width cards.
- Avoid measuring a page before CUI injects its custom elements.

## Cards move when a pager changes page

The pager wrapper follows the active page height. Measure all pages and hold the wrapper at the tallest page height. Recalculate that value from a `ResizeObserver` after responsive width changes.

## JSON save returns `WinError 5`

Windows denied file replacement. Common causes include antivirus scanning, sync software, and another process holding the JSON file.

- Use a process lock around writes.
- Write a unique temporary file.
- Keep the original file when replacement fails.
- Report the file path and permission error.
- Close editors or sync tools that hold the file.

Do not clear stored tokens after a save error.

## Discord gateway closes with code 1006

Code 1006 reports an abnormal transport closure. It does not prove the token is invalid.

- Check the network, VPN, proxy, and firewall.
- Use Discord's gateway heartbeat from the HELLO payload.
- Disable aiohttp's separate WebSocket ping timer for Discord gateway sessions.
- Add capped reconnect backoff.
- Start saved accounts with spacing between IDENTIFY requests.
- Stop retrying after Discord rejects authentication or account verification.

Explain account requirements in the UI when Discord reports phone, email, or verification limits.

## Managed token cannot join a voice channel

Check the account before changing gateway code:

- The account belongs to the server.
- The account can view and connect to the channel.
- The account completed Discord verification requirements.
- The token represents the expected account.
- Discord accepted the gateway session.

Show the account-specific error in the managed-account row. A single generic toast does not identify the failing token.

## Blocking request freezes Nighty

Use `aiohttp` for HTTP calls. Move synchronous libraries to an executor:

```python
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, blocking_function)
```

Replace `time.sleep()` with `await asyncio.sleep()` inside async functions.

## Share a useful bug report

Include:

- Nighty version
- script version
- browser or private-tab environment
- action that failed
- sanitized console error
- whether the failure survives a Nighty restart

Remove account tokens, webhook URLs, cookies, interaction tokens, and private channel data.
