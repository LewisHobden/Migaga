class Tools:
    async def ifNoneReplaceWith(self, test_string, replace_string):
        if None == test_string:
            return replace_string

        return test_string
