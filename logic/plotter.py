def plot_lap_telemetry(lap, speed_canvas, throttle_canvas, brake_canvas, gear_canvas):
    tel = lap.get_car_data().add_distance()

    speed_canvas.ax.clear()
    speed_canvas.ax.plot(tel['Distance'], tel['Speed'], color='deepskyblue')
    speed_canvas.ax.set(title='Speed vs Distance', xlabel='Distance (m)', ylabel='Speed (km/h)')
    speed_canvas.ax.grid(True)
    speed_canvas.draw()

    throttle_canvas.ax.clear()
    throttle_canvas.ax.plot(tel['Distance'], tel['Throttle'], color='lime')
    throttle_canvas.ax.set(title='Throttle', xlabel='Distance (m)', ylabel='Throttle (%)')
    throttle_canvas.ax.grid(True)
    throttle_canvas.draw()

    brake_canvas.ax.clear()
    brake_canvas.ax.plot(tel['Distance'], tel['Brake'], color='red')
    brake_canvas.ax.set(title='Brake', xlabel='Distance (m)', ylabel='Brake (boolean)')
    brake_canvas.ax.grid(True)
    brake_canvas.draw()

    gear_canvas.ax.clear()
    gear_canvas.ax.plot(tel['Distance'], tel['nGear'], color='orange')
    gear_canvas.ax.set(title='Gear', xlabel='Distance (m)', ylabel='Gear')
    gear_canvas.ax.grid(True)
    gear_canvas.draw()

def plot_comparison_telemetry(session, drivers, speed_canvas, throttle_canvas, brake_canvas, gear_canvas):
    if not drivers:
        return

    colors = ['dodgerblue', 'orangered', 'limegreen', 'purple', 'gold']

    # Clear all
    for canvas in [speed_canvas, throttle_canvas, brake_canvas, gear_canvas]:
        canvas.ax.clear()

    for i, driver in enumerate(drivers):
        try:
            lap = session.laps.pick_driver(driver).pick_fastest()
            tel = lap.get_car_data().add_distance()
            c = colors[i % len(colors)]

            speed_canvas.ax.plot(tel['Distance'], tel['Speed'], label=driver, color=c)
            throttle_canvas.ax.plot(tel['Distance'], tel['Throttle'], label=driver, color=c)
            brake_canvas.ax.plot(tel['Distance'], tel['Brake'], label=driver, color=c)
            gear_canvas.ax.plot(tel['Distance'], tel['nGear'], label=driver, color=c)

        except Exception as e:
            print(f"[Comparison Plot Error] {driver}: {e}")

    for canvas, title, ylab in zip(
        [speed_canvas, throttle_canvas, brake_canvas, gear_canvas],
        ["Speed Comparison", "Throttle Comparison", "Brake Comparison", "Gear Comparison"],
        ["Speed (km/h)", "Throttle (%)", "Brake (0/1)", "Gear"]):

        canvas.ax.set_title(title)
        canvas.ax.set_xlabel("Distance (m)")
        canvas.ax.set_ylabel(ylab)
        canvas.ax.legend()
        canvas.ax.grid(True)
        canvas.draw()
