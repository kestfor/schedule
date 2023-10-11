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


def get_schedule(data: dict) -> dict:
    res = {}
    start = 8
    end = 24
    full_time = end - start
    data_list = [(key, data[key]) for key in data]
    reserved_time = sum([item[-1] for item in data_list])
    free_time = full_time - reserved_time
    if reserved_time > full_time:
        raise OverflowError
    data_list.sort(key=lambda x: (x[-1], x[0]))
    res_list = [[] for _ in range(len(data_list))]
    curr_time = start
    time_for_one_gap = 0
    if free_time == 0:
        gaps = 0
    else:
        gaps = len(data) - 1
        if gaps != 0:
            time_for_one_gap = free_time // gaps
            while time_for_one_gap == 0 and gaps > 0:
                gaps -= 1
                time_for_one_gap = free_time // gaps
    end_time = start + reserved_time + gaps * time_for_one_gap
    for i in range(len(data_list)):
        if i % 2 == 0:
            res_list[i // 2] = [data_list[i][0], [curr_time, curr_time + data_list[i][1]]]
            curr_time = curr_time + data_list[i][1]
            if gaps > 0:
                curr_time += time_for_one_gap
                gaps -= 1
        else:
            res_list[len(data_list) - (i + 1) // 2] = [data_list[i][0], [end_time - data_list[i][1], end_time]]
            end_time -= data_list[i][1]
            if gaps > 0:
                end_time -= time_for_one_gap
                gaps -= 1
    for item in res_list:
        res[item[0]] = item[1]
    return res


