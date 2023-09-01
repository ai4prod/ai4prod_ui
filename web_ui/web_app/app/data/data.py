
class Data:
    """
    Class used to save temporary data inside application
    currentDataset is used to save globally which dataset i currently visualize in /dataset_statistics route
    """

    def __init__(self) -> None:

        self.epoch_counter = 0
        self.loss = {}
        self.dataset_change = False
        self.current_dataset_id = 0
