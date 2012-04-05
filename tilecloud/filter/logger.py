class Logger(object):

    def __init__(self, logger, level, msgformat, *args, **kwargs):
        self.logger = logger
        self.level = level
        self.msgformat = msgformat
        self.args = args
        self.kwargs = kwargs

    def __call__(self, tile):
        if tile is not None:
            variables = dict()
            variables.update(tile.__dict__)
            variables.update(tile.tilecoord.__dict__)
            self.logger.log(self.level, self.msgformat % variables,
                            *self.args, **self.kwargs)
        return tile
