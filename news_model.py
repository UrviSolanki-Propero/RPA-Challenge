class Model:
    def __init__(self, data: tuple) -> None:
        """Initializes the model and stores the tuple in its variables.
        """
        self.title_list = data[0]
        self.date_list = data[1]
        self.description_list = data[2]
        self.image_file_list = data[3]
        self.money_present_list = data[4]
        self.count_phrase_list = data[5]
