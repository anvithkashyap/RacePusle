import fastf1

def load_session_data(year, round_number, session_type):
    session = fastf1.get_session(year, round_number, session_type)
    session.load()
    return session

def get_driver_laps(session, driver):
    return session.laps.pick_driver(driver)