# Native UI scripting

Nighty scripts can add interactive tabs to the Nighty interface. Native UI scripting supplies the layout tree, form controls, tables, callbacks, and toast notifications. It does not require browser HTML or JavaScript.

This guide is adapted from [ThatDudePyro's Nighty UI Scripting Framework Reference v1.1](https://github.com/ThatDudePyro/UI-Scripting-Docs). The wording and examples here were rewritten for the NightyScript v5 documentation.

## Required structure

Build components through their parent objects:

```text
Tab
└── CardContainer
    ├── Card
    │   ├── UI element
    │   └── Group
    │       └── UI element
    └── CardContainer
```

The rules are strict:

- Give each tab a unique name no longer than 36 characters.
- Create at least one container for every tab.
- Create cards through a container.
- Create groups through a card or another group.
- Create UI elements through a card or group.
- Do not place a card inside another card.
- Keep nested containers to three levels or fewer.
- Call `tab.render()` after the complete UI tree is defined.

Direct construction is not supported:

```python
# Wrong
card = Card()
button = UI.Button()

# Correct
card = container.create_card()
button = card.create_ui_element(UI.Button, label="Save")
```

## Small working tab

```python
@nightyScript(
    name="UI Starter",
    author="Your Name",
    description="Small native UI example",
    usage="Open the UI Starter tab"
)
def ui_starter():
    tab = Tab(name="UI Starter", icon="star", gap=4)
    container = tab.create_container(
        type="rows",
        width="full",
        height="auto",
        gap=4
    )
    card = container.create_card(
        type="rows",
        width="full",
        height="auto",
        gap=3
    )

    card.create_ui_element(
        UI.Text,
        content="UI Starter",
        size="xl",
        weight="bold"
    )
    name_input = card.create_ui_element(
        UI.Input,
        label="Name",
        placeholder="Enter a name",
        full_width=True
    )
    output = card.create_ui_element(
        UI.Text,
        content="Nothing saved yet."
    )
    save_button = card.create_ui_element(
        UI.Button,
        label="Save",
        color="primary"
    )

    def save_name():
        value = str(name_input.value or "").strip()
        if not value:
            name_input.invalid = True
            name_input.error_message = "Enter a name."
            return
        name_input.invalid = False
        output.content = f"Saved: {value}"
        tab.toast("Saved", value, "SUCCESS")

    save_button.onClick = save_name
    tab.render()

ui_starter()
```

## Tab

`Tab` is the root of a custom page.

```python
tab = Tab(
    name="Task Queue",
    icon="inbox",
    gap=4,
    title="Tasks"
)
```

Supported fields:

- `name`: required unique tab name, up to 36 characters.
- `icon`: one of Nighty's built-in icon names.
- `gap`: spacing between top-level containers, from `0` to `10`.
- `title`: optional heading above the tab content.

Main methods:

```python
container = tab.create_container(type="rows")
tab.toast("Saved", "The settings were updated.", "SUCCESS")
tab.render()
```

Toast types are `INFO`, `ERROR`, and `SUCCESS`. Pass the title, description, and type.

### Built-in tab icons

```text
report, chart, two_way, inbox, star, search, variants, message,
users, history, clean, magic, eraser, convert, cloud, calc,
calendar, key, gift, trophy, book, sun, cart, pill, bookmark,
mail, bear, heart, music, umbrella, tube, palette, lock, fire,
preferences, power, share, bell, trash, nitro
```

## CardContainer

A container controls how cards and nested containers are arranged.

```python
container = tab.create_container(
    type="columns",
    width="full",
    height="auto",
    gap=4
)
```

- `type="columns"` places children side by side.
- `type="rows"` stacks children vertically.
- `width` and `height` accept `"auto"` or `"full"`.
- `gap` accepts values from `0` to `10`.

Containers can create cards and nested containers:

```python
card = container.create_card()
nested = container.create_container(type="rows")
```

## Card

A card holds UI elements and groups.

```python
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

Alignment accepts `start`, `center`, or `end`. Set `disallow_shrink=True` when a card must keep its intended size inside a crowded container.

Cards expose:

```python
group = card.create_group(type="columns")
text = card.create_ui_element(UI.Text, content="Ready")
```

## Group

Groups arrange controls inside a card. They can also contain nested groups.

```python
actions = card.create_group(
    type="columns",
    vertical_align="center",
    horizontal_align="start",
    gap=2,
    full_width=True
)

save = actions.create_ui_element(UI.Button, label="Save")
reset = actions.create_ui_element(UI.Button, label="Reset", variant="bordered")
```

Use groups for related controls. Use containers for card-level page structure.

## Text

```python
status = card.create_ui_element(
    UI.Text,
    content="Status: idle",
    size="base",
    weight="medium",
    color="#ffffff",
    align="left",
    margin="m-0",
    visible=True
)
```

Text sizes are `tiny`, `sm`, `base`, `lg`, `xl`, and `2xl`. Weight accepts `thin`, `light`, `normal`, `medium`, `bold`, `extrabold`, and `black`.

Update text after rendering by assigning its attributes:

```python
status.content = "Status: connected"
status.weight = "bold"
```

## Button

```python
button = card.create_ui_element(
    UI.Button,
    label="Connect",
    variant="solid",
    color="primary",
    size="md",
    full_width=False,
    disabled=False,
    loading=False,
    visible=True
)
```

Variants include `solid`, `bordered`, `ghost`, `light`, `flat`, and `cta`. Standard colors include `primary`, `default`, `success`, and `danger`.

Callbacks can be synchronous or asynchronous:

```python
async def connect():
    button.loading = True
    try:
        await perform_connection()
    finally:
        button.loading = False

button.onClick = connect
```

## Input

```python
channel_input = card.create_ui_element(
    UI.Input,
    label="Channel ID",
    placeholder="123456789012345678",
    value="",
    description="Paste a voice channel ID.",
    show_clear_button=True,
    invalid=False,
    disabled=False,
    readonly=False,
    required=True,
    full_width=True,
    error_message="",
    visible=True
)
```

Listen for value changes with `onInput`:

```python
def validate_channel(value):
    value = str(value or "").strip()
    channel_input.invalid = bool(value and not value.isdigit())
    channel_input.error_message = "Use a numeric channel ID." if channel_input.invalid else ""

channel_input.onInput = validate_channel
```

Read the current value from `channel_input.value`.

## Toggle

```python
notifications = card.create_ui_element(
    UI.Toggle,
    label="Notifications",
    checked=False,
    disabled=False,
    visible=True
)

def set_notifications(checked):
    updateConfigData("example_notifications", bool(checked))

notifications.onChange = set_notifications
```

## Checkbox

```python
confirm = card.create_ui_element(
    UI.Checkbox,
    label="I understand",
    checked=False,
    disabled=False,
    invalid=False,
    visible=True
)

confirm.onChange = lambda checked: print(f"Confirmed: {checked}")
```

## Select

```python
server_select = card.create_ui_element(
    UI.Select,
    label="Server",
    items=[
        {"id": "guild-1", "title": "First server"},
        {"id": "guild-2", "title": "Second server", "iconUrl": "https://example.com/icon.png"}
    ],
    selected_items=[],
    disabled_items=[],
    mode="single",
    description="Choose a server.",
    loading=False,
    disabled=False,
    invalid=False,
    error_message="",
    full_width=True,
    visible=True
)

def server_changed(selected_items):
    selected_id = selected_items[0] if selected_items else None
    print(f"Selected server: {selected_id}")

server_select.onChange = server_changed
```

Use unique string IDs for every item. Set `mode="multiple"` when more than one item can be selected.

## Image

```python
image = card.create_ui_element(
    UI.Image,
    url="https://example.com/image.png",
    alt="Preview",
    circle=False,
    shadow=False,
    width="96px",
    height="96px",
    rounded="lg",
    fill_type="cover",
    border_color="#ffffff",
    border_width=0,
    visible=True
)
```

`fill_type` accepts `cover` or `contain`. Width and height accept CSS-like values such as `96px`, `50%`, or `auto`.

## Table

Tables support text, tag, and button columns.

```python
def remove_row():
    print("Remove clicked")

table = card.create_ui_element(
    UI.Table,
    columns=[
        {"type": "text", "label": "Account"},
        {"type": "tag", "label": "Status"},
        {
            "type": "button",
            "label": "Action",
            "buttons": [
                {"label": "Remove", "color": "danger", "onClick": remove_row}
            ]
        }
    ],
    rows=[
        {
            "id": "account-1",
            "cells": [
                {"text": "Primary", "subtext": "123456789012345678"},
                {"text": "Ready", "color": "green"},
                {}
            ]
        }
    ],
    search=True,
    items_per_page=25,
    selectable=False,
    visible=True
)
```

Each row needs a unique `id`. The number and order of cells must match the columns.

Selection callbacks receive row IDs:

```python
def selection_changed(row_ids):
    print(f"Selected rows: {row_ids}")

table.onSelectionChange = selection_changed
```

Replace the rows after rendering with:

```python
table.rows = new_rows
```

## Shared layout fields

### Gap

`gap` controls spacing between children. It accepts values from `0` to `10` on tabs, containers, cards, and groups.

### Margin

UI elements accept Tailwind-style margin strings:

```python
margin="m-4"   # all sides
margin="mx-3"  # left and right
margin="mt-2"  # top
margin="mb-2"  # bottom
```

### Visibility

Native elements expose a `visible` property:

```python
details.visible = False
details.visible = True
```

Use visibility for conditional sections instead of rebuilding the whole tab.

## Responsive layouts

Nighty can show the same tab in the desktop app and a browser. Keep layouts usable at narrow widths:

- Prefer a top-level `rows` container for pages with many cards.
- Use `width="full"` for forms and tables.
- Keep critical controls in small groups instead of one long row.
- Avoid fixed pixel widths unless an image needs them.
- Keep container nesting shallow.
- Use `height="auto"` for content that changes at runtime.
- Test the tab after a browser refresh and at mobile width.

Native `columns` layouts may become crowded on phones. Use separate cards or a rows layout when labels and buttons need more room.

## State and callbacks

Create every element before calling `tab.render()`. Keep references to elements that callbacks need to update:

```python
status = card.create_ui_element(UI.Text, content="Idle")
run_button = card.create_ui_element(UI.Button, label="Run")

async def run_job():
    run_button.disabled = True
    status.content = "Running"
    try:
        await do_work()
        status.content = "Complete"
        tab.toast("Complete", "The job finished.", "SUCCESS")
    except Exception as error:
        status.content = "Failed"
        print(f"[UI Example] Run failed: {error}", type_="ERROR")
        tab.toast("Failed", str(error), "ERROR")
    finally:
        run_button.disabled = False

run_button.onClick = run_job
```

Avoid blocking work inside callbacks. Use async libraries or move blocking functions to an executor.

## Common failures

### The tab does not appear

Check that:

- the decorated script function is called;
- the tab has at least one container;
- `tab.render()` runs after the UI tree is complete;
- the tab name is unique and no longer than 36 characters.

### A component raises an attribute error

Check its parent. Cards come from containers. Groups and UI elements come from cards or groups. Do not instantiate framework classes directly.

### A select or table behaves unpredictably

Make item and row IDs unique strings. Ensure table cells match the column order.

### A button appears stuck

Reset `loading` and `disabled` in a `finally` block so errors do not leave the control locked.

### The layout breaks on mobile

Replace crowded column groups with rows, use full-width controls, remove fixed widths, and reduce nested containers.

## Native UI or CUI

Use native UI scripting first. It works with Nighty's component model and requires less browser-specific code.

Use [CUI](cui.md) when the native elements cannot express the control you need, such as a custom slider, pager, modal, or specialized HTML layout. CUI still starts with the same `Tab` → `CardContainer` → `Card` hierarchy.

## Source and credits

- [ThatDudePyro/UI-Scripting-Docs](https://github.com/ThatDudePyro/UI-Scripting-Docs), Nighty UI Scripting Framework Reference v1.1
- [Nighty](https://nighty.one/)

[Back to the main documentation](../README.md)
