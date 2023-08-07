from app.home import data_instance

def event_counter(string):
    global data_instance
    data_instance.epoch_counter = string
    print(f"EVENT TYPE {string}")
    print(f"data_instance {data_instance.epoch_counter}")