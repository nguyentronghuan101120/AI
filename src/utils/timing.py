import time


class measure_time:
    def __init__(self, label="Operation"):
        self.label = label

    def __enter__(self):
        print(f"\nStart: {self.label}")
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        end = time.time()
        print(f"\n{self.label} took {end - self.start:.2f} seconds\n")
