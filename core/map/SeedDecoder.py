# Adapted from Lda2138/SheepSolver/map_protocol.py (AGPL-3.0).
from core.map.BinaryMapDecoder import fields, varint

def valid_seed(seed):
    return (isinstance(seed, list) and len(seed) == 4 and
            all(isinstance(x, int) and not isinstance(x, bool) and -2**31 <= x <= 2**32-1 for x in seed) and any(seed))


def decode_seed(raw):
    seed, code, seed2 = [], None, None
    for number, wire, value in fields(raw):
        if number == 1 and wire == 0:
            code = value
        elif number == 2 and wire == 0:
            seed.append(value)
        elif number == 2 and wire == 2:
            at = 0
            while at < len(value):
                item, at = varint(value, at)
                seed.append(item)
        elif number == 3 and wire == 2:
            seed2 = value.decode('utf-8')
        else:
            raise ValueError('种子消息字段不匹配')
    if code != 1 or not valid_seed(seed):
        raise ValueError('未获得成功的真实种子响应')
    return {'map_seed': seed, 'map_seed_2': seed2}

