import collections


def mode(data):
    data_len = len(data)
    if data_len == 0:
        return None

    table = collections.Counter(iter(data)).most_common()
    if table:
        maxfreq = table[0][1]
        for i in range(1, len(table)):
            if table[i][1] != maxfreq:
                table = table[:i]
                break

    return table[0][0]
