class EdgeMapper:
    def __init__(self, session):
        self.session = session

    def batch_create_edges(self, adjacencies):
        return {"created": 0, "updated": 0}
