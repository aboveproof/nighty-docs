# CUI and custom Nighty tabs

Nighty's UI API creates tabs, containers, cards, groups, and standard controls. CUI extends that API with custom HTML elements and callable overlays.

Read [Native UI scripting](ui-scripting.md) first if the page only needs Nighty's built-in controls.

Source: [vahrervert/cui](https://github.com/vahrervert/cui)

## Native hierarchy

Create each object through its parent:

```text
Tab
└── CardContainer
    ├── Card
    │   ├── UI element
    │   └── Group
    │       └── UI element
    └── CardContainer
```

```python
tab = Tab(name="Account Tools", icon="users", gap=4)
container = tab.create_container(type="rows", width="full", height="auto", gap=4)
card = container.create_card(type="rows", width="full", height="auto", gap=3)
group = card.create_group(type="columns", gap=2, full_width=True)
group.create_ui_element(UI.Text, content="Ready")
tab.render()
```

Do not instantiate `CardContainer`, `Card`, `Group`, or `UI` elements by calling their classes.

## Tab

```python
tab = Tab(
    name="Account Tools",
    icon="users",
    gap=4,
    title="Account Tools"
)
```

Tab names must be unique and fit Nighty's 36-character limit.

Common icons:

`report`, `chart`, `inbox`, `star`, `search`, `message`, `users`, `history`, `clean`, `magic`, `cloud`, `calendar`, `key`, `gift`, `book`, `music`, `palette`, `lock`, `preferences`, `power`, `share`, `bell`, `trash`

Render the tab after creating its controls:

```python
tab.render()
```

## Containers and cards

```python
container = tab.create_container(
    type="columns",
    width="full",
    height="auto",
    gap=4
)

card = container.create_card(
    type="rows",
    width="full",
    height="auto",
    vertical_align="start",
    horizontal_align="start",
    gap=3,
    disallow_shrink=False
)
```

Use `columns` for a horizontal layout and `rows` for a vertical layout. `auto` follows content size. `full` uses available space.

Mix an `auto` child with a `full` child when one card needs a content width and the other should fill the row. Two `full` cards share the row when CUI can measure both cards before paint.

Keep container nesting under three levels. Use groups inside cards instead of nesting cards.

## Groups

```python
actions = card.create_group(
    type="columns",
    gap=2,
    full_width=True
)
```

Groups organize controls inside a card. Groups can contain nested groups and UI elements.

## Standard controls

### Text

```python
title = card.create_ui_element(
    UI.Text,
    content="Account status",
    size="lg",
    weight="bold",
    align="left"
)

title.content = "Account connected"
```

Sizes: `tiny`, `sm`, `base`, `lg`, `xl`, `2xl`

Weights: `thin`, `light`, `normal`, `medium`, `bold`, `extrabold`, `black`

### Button

```python
button = card.create_ui_element(
    UI.Button,
    label="Refresh",
    variant="bordered",
    color="default",
    disabled=False
)

async def refresh():
    button.loading = True
    try:
        await load_accounts()
    finally:
        button.loading = False

button.onClick = refresh
```

Variants: `solid`, `bordered`, `ghost`, `light`, `flat`, `cta`

Colors: `primary`, `default`, `success`, `danger`

### Input

```python
name_input = card.create_ui_element(
    UI.Input,
    label="Account name",
    placeholder="Enter a name",
    show_clear_button=True,
    full_width=True
)

def validate_name(value):
    name_input.invalid = not str(value or "").strip()
    name_input.error_message = "Enter an account name." if name_input.invalid else None

name_input.onInput = validate_name
```

### Toggle

```python
alerts_toggle = card.create_ui_element(
    UI.Toggle,
    label="Connection alerts",
    checked=True
)

async def update_alerts(checked):
    updateConfigData("account_tools_alerts", bool(checked))

alerts_toggle.onChange = update_alerts
```

### Select

```python
server_select = card.create_ui_element(
    UI.Select,
    label="Server",
    items=[
        {"id": "1", "title": "Support", "iconUrl": "https://example.com/icon.png"},
        {"id": "2", "title": "Projects"}
    ],
    selected_items=[],
    disabled_items=[],
    mode="single",
    full_width=True
)
```

Each item needs a unique string ID.

### Table

```python
table = card.create_ui_element(
    UI.Table,
    columns=[
        {"type": "text", "label": "Account"},
        {"type": "tag", "label": "Status"},
        {"type": "button", "label": "Action", "buttons": [
            {"label": "Remove", "color": "danger", "onClick": remove_account}
        ]}
    ],
    rows=[
        {
            "id": "account-1",
            "cells": [
                {"text": "Backup", "subtext": "ID: 123"},
                {"text": "Ready", "color": "green"},
                {}
            ]
        }
    ],
    search=True,
    items_per_page=10,
    selectable=False
)
```

Row cell order must match the columns.

## Toasts

```python
tab.toast("Account saved", "Backup is ready.", "SUCCESS")
tab.toast("Token required", "Paste a Discord token.", "ERROR")
tab.toast("Connecting", "Discord is opening the session.", "INFO")
```

Pass title, description, and type.

## Install CUI

The CUI bootstrap patches `Card.create_ui_element`, `Group.create_ui_element`, and `Tab.render`.

1. Copy the CUI bootstrap into the decorated script function.
2. Keep its indentation inside that function.
3. Place custom `@cui_new` classes after the bootstrap.
4. Create custom elements through a card or group.
5. Call `tab.render()` after the complete UI tree exists.

CUI registers its Python callback through Nighty's callback store and injects the HTML template into the browser page.

## Custom element

```python
@cui_new(type="element")
class ValueMeter:
    _init_params = ["self", "label", "value", "on_change"]

    def __init__(self, label="Level", value=50, on_change=None):
        self.funcs = [on_change]
        self.html = """
            <label style="display:flex;flex-direction:column;gap:6px;width:100%;">
                <span style="font-size:13px;font-weight:600;">${data.label}</span>
                <input
                    type="range"
                    min="0"
                    max="100"
                    value="${data.value}"
                    onchange="${on_change}"
                >
            </label>
        """

def update_level(value):
    updateConfigData("meter_level", int(value))

meter = card.create_ui_element(
    UI.ValueMeter,
    label="Level",
    value=getConfigData().get("meter_level", 50),
    on_change=update_level
)
```

`_init_params` lists template properties and callbacks. CUI replaces `${data.name}` with property values and `${callback_name}` with a browser-to-Python callback.

Keep callback values simple. CUI sends the element value as text.

## Callable overlay

Use a callable for a modal or overlay that Nighty opens on demand:

```python
@cui_new(type="callable", name="ConfirmDialog")
class ConfirmDialog:
    _init_params = ["self", "message", "on_confirm", "on_close"]

    def __init__(self, message="Continue?", on_confirm=None, on_close=None):
        self.funcs = [on_confirm, on_close]
        self.html = """
            <div style="position:fixed;inset:0;display:grid;place-items:center;background:rgba(0,0,0,.68);">
                <section style="width:min(420px,90vw);padding:20px;border-radius:12px;background:#111827;">
                    <p>${data.message}</p>
                    <div style="display:flex;gap:8px;justify-content:flex-end;">
                        <button onclick="${on_close}">Cancel</button>
                        <button onclick="${on_confirm}">Confirm</button>
                    </div>
                </section>
            </div>
        """

tab.confirmdialog(
    message="Remove this account?",
    on_confirm=remove_account,
    on_close=lambda: None
)
```

The CUI bootstrap adds callable methods to `Tab` with lowercase names.

## Space and page markers

Custom layouts can add a fixed spacer:

```python
@cui_new(type="element")
class Space:
    _init_params = ["self", "height"]

    def __init__(self, height="12px"):
        self.html = (
            '<div style="width:100%;height:${data.height};'
            'min-height:${data.height};pointer-events:none;"></div>'
        )

card.create_ui_element(UI.Space, height="20px")
```

A pager can mark page boundaries with a hidden element:

```python
@cui_new(type="element")
class PageMarker:
    _init_params = ["self", "page_id", "pager_id", "max_height"]

    def __init__(self, page_id=None, pager_id=None, max_height=None):
        self.html = (
            '<div id="${data.page_id}" class="cui-page-marker" '
            'data-pager-id="${data.pager_id}" '
            'data-max-height="${data.max_height}" '
            'style="display:none!important;"></div>'
        )
```

Keep a pager wrapper at a stable height when its pages have different content heights. Measuring the tallest page prevents neighboring cards from moving during a page change.

## Reload handling

A browser refresh creates a new JavaScript window. The Python script may remain loaded.

The CUI bootstrap should reinstall templates on Socket.IO connect:

```python
def reinstall_cui():
    evaluate_js(JS_CUI)
    # Register element templates after installing the runtime.

@socketio.on("connect")
def restore_cui():
    reinstall_cui()
```

Avoid registering duplicate Socket.IO handlers after a script reload. Store handler ownership or remove the previous handler before adding a replacement.

Mutation observers should process new placeholders and leave rendered elements alone. Mark installed observers on `window` so the next install can disconnect them.

## Layout rules

- Use `height="auto"` for content cards.
- Use `disallow_shrink=True` for narrow controls that must keep their width.
- Give side-by-side cards a stable flex basis.
- Keep table and select IDs unique.
- Set button loading states around async work.
- Add input validation near the field.
- Use one accent color and Nighty's surface colors.
- Test the tab after a browser refresh and a script reload.

## Debugging

### Raw `__CUI__` text appears

The browser runtime did not inject the template. Reinstall `JS_CUI`, register the templates, and run the placeholder scan after the page renders.

### Callback does not run

Check `_init_params`, `self.funcs`, the `${callback_name}` placeholder, and callback-store registration.

### Card collapses after pagination

CUI measured hidden content as zero width or a short height. Give the card a full flex basis and hold the wrapper at the tallest page height.

### UI works after restarting Nighty but fails after refresh

The script restored Python state but did not restore the browser runtime. Add a Socket.IO connect handler and a browser-page recovery pass.

## Example

See [`cui_custom_element_example.py`](../example-scripts/cui_custom_element_example.py).
