class ActivitiesParser:

    @staticmethod
    def check_format(data: str) -> bool:
        import re
        for line in data.split('\n'):
            line.strip()
            if len(line) > 0:
                match = re.fullmatch("[A-Za-zА-Яa-я ]* {0,}- {0,}\d", line)
                if not match:
                    return False
        return True

    @staticmethod
    def parse(data: str) -> dict:
        if not ActivitiesParser.check_format(data):
            raise SyntaxError("wrong string format")
        lines = data.split('\n')
        res = {}
        for line in lines:
            line.strip()
            if len(line) > 0:
                activity, time = line.split('-')
                activity = activity.strip()
                time = int(time.strip())
                res[activity] = time
        return res


def alg(d: dict):
    raise OverflowError