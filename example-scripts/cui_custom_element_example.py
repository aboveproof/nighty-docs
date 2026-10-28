@nightyScript(
    name="CUI Meter Example",
    author="rico",
    description="Custom CUI range control with saved state",
    usage="UI script"
)
def cui_meter_example():
    """
    CUI METER EXAMPLE

    SETUP:
    Copy the CUI bootstrap from vrahervert/cui into the marked location.
    Keep the bootstrap indented inside this function.
    """

    # Paste the CUI bootstrap here.

    @cui_new(type="element")
    class ValueMeter:
        _init_params = ["self", "label", "value", "on_change"]

        def __init__(self, label="Level", value=50, on_change=None):
            self.funcs = [on_change]
            self.html = """
                <label style="display:flex;flex-direction:column;gap:8px;width:100%;">
                    <span style="display:flex;justify-content:space-between;font-size:13px;font-weight:600;">
                        <span>${data.label}</span>
                        <output>${data.value}</output>
                    </span>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value="${data.value}"
                        oninput="this.previousElementSibling.querySelector('output').textContent=this.value"
                        onchange="${on_change}"
                        style="width:100%;accent-color:#4a6d88;"
                    >
                </label>
            """

    tab = Tab(name="CUI Meter", icon="chart", gap=4)
    container = tab.create_container(type="rows", width="full", height="auto", gap=4)
    card = container.create_card(type="rows", width="full", height="auto", gap=3)

    card.create_ui_element(UI.Text, content="Saved level", size="lg", weight="bold")

    def update_level(value):
        try:
            level = max(0, min(100, int(float(value))))
        except (TypeError, ValueError):
            tab.toast("Invalid level", "Choose a number from 0 to 100.", "ERROR")
            return
        updateConfigData("cui_meter_level", level)
        tab.toast("Level saved", str(level), "SUCCESS")

    card.create_ui_element(
        UI.ValueMeter,
        label="Level",
        value=getConfigData().get("cui_meter_level", 50),
        on_change=update_level
    )

    tab.render()


cui_meter_example()
