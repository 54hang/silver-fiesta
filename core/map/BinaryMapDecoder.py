# Map decoding adapted from Lda2138/SheepSolver map_protocol.py (AGPL-3.0).
# Source: https://github.com/Lda2138/SheepSolver/blob/HEAD/map_protocol.py
"""Decode the map and seed schemas verified against the installed game package."""
import copy
import json
import re

from core.data.ShuffleHelper import ShuffleHelper


def varint(data, at):
    value = 0
    for shift in range(0, 70, 7):
        if at >= len(data):
            raise ValueError('截断的 Protobuf')
        byte = data[at]
        at += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, at
    raise ValueError('Protobuf 整数过长')


def fields(data):
    at = 0
    while at < len(data):
        tag, at = varint(data, at)
        number, wire = tag >> 3, tag & 7
        if number == 0:
            raise ValueError('非法 Protobuf 字段')
        if wire == 0:
            value, at = varint(data, at)
        elif wire == 2:
            length, at = varint(data, at)
            if at + length > len(data):
                raise ValueError('非法 Protobuf 长度')
            value = data[at:at + length]
            at += length
        elif wire in (1, 5):
            length = 8 if wire == 1 else 4
            if at + length > len(data):
                raise ValueError('截断字段')
            value = data[at:at + length]
            at += length
        else:
            raise ValueError('不支持的 Protobuf wire type')
        yield number, wire, value


def signed32(value):
    value &= 0xffffffff
    return value - 0x100000000 if value & 0x80000000 else value


def decode_node(data):
    node = {key: 0 for key in ('type', 'rolNum', 'rowNum', 'layerNum', 'moldType', 'metaType', 'metaData')}
    node['id'] = ''
    names = {2: 'type', 3: 'rolNum', 4: 'rowNum', 5: 'layerNum', 6: 'moldType', 7: 'metaType', 8: 'metaData'}
    for number, wire, value in fields(data):
        if number == 1 and wire == 2:
            node['id'] = value.decode('utf-8')
        elif number in names and wire == 0:
            node[names[number]] = signed32(value)
    if not re.fullmatch(r'\d+-\d+-\d+', node['id']):
        raise ValueError('地图牌编号不合法')
    return node


def decode_gold(data):
    result={'collectCount':0,'blockList':[]}
    for number,wire,value in fields(data):
        if number==1 and wire==0:result['collectCount']=signed32(value)
        elif number==2 and wire==2:
            block={'val':0,'count':0}
            for n,w,v in fields(value):
                if n in (1,2) and w==0:block['val' if n==1 else 'count']=signed32(v)
            result['blockList'].append(block)
    return result


def validate_geometry(data):
    levels = data.get('levelData')
    if not isinstance(levels, dict) or not levels:
        raise ValueError('缺少地图层级')
    ids = set()
    count = 0
    for level, cards in levels.items():
        int(level)
        for card in cards:
            if card['id'] in ids:
                raise ValueError('重复牌编号')
            ids.add(card['id'])
            if not re.fullmatch(r'\d+-\d+-\d+', card['id']):
                raise ValueError('地图牌编号不合法')
            if [int(x) for x in card['id'].split('-')] != [int(level), card['rolNum'], card['rowNum']]:
                raise ValueError('牌编号与层级不一致')
            for key in ('type', 'rolNum', 'rowNum'):
                if not isinstance(card[key], int) or card[key] < 0:
                    raise ValueError('牌类型或坐标无效')
            count += 1
    if count < 3 or count > 3000:
        raise ValueError('地图牌数量异常')
    return count


def decode_map(raw):
    if raw.lstrip().startswith(b'{'):
        result = json.loads(raw.decode('utf-8-sig'))
        validate_geometry(result)
        return result
    errors = []
    # Installed client removes exactly 21 bytes before GameMap.decode.
    for data in (raw[21:], raw):
        try:
            result = {'blockTypeData': {}, 'levelData': {}}
            for number, wire, value in fields(data):
                if number in (1, 2, 3, 8) and wire == 0:
                    result[{1: 'widthNum', 2: 'heightNum', 3: 'levelKey', 8: 'cdNum'}[number]] = signed32(value)
                elif number in (4, 5, 7) and wire == 2:
                    item = {n: v for n, _, v in fields(value)}
                    key = item.get(1, b'').decode('utf-8')
                    if not key.isdigit() or 2 not in item:
                        raise ValueError('地图索引错误')
                    if number == 5:
                        cards = [decode_node(v) for n, w, v in fields(item[2]) if n == 1 and w == 2]
                        result['levelData'][key] = cards
                    else:
                        target = 'blockTypeData' if number == 4 else 'blockTypeCfg'
                        result.setdefault(target, {})[key] = signed32(item[2])
                elif number == 6 and wire == 2 and value:
                    result['_has_gold_rules'] = True
                    result['goldBlockData']=decode_gold(value)
            validate_geometry(result)
            return result
        except (ValueError, TypeError, UnicodeError) as exc:
            errors.append(str(exc))
    raise ValueError('地图解码失败：' + '; '.join(errors))

