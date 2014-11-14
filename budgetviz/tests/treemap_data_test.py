from budgetviz import treemap_data
import datetime

def test_jsoned():
    assert treemap_data.jsoned("hey", [
        {"description": 'you', 'cost': 12.7, 'category': 'hey',
         'date': datetime.datetime(2001, 2, 3)},
        {"description": 'guy', 'cost': 11.3, 'category': 'hey',
         'date': datetime.datetime(2002, 3, 4)},
    ]) == \
    '''{"name": "hey", "children": [
    {"name": "you", "size": 12.7, "category": "hey", "category_total": 24.0, "date": "Feb. 3, 2001"},
    {"name": "guy", "size": 11.3, "category": "hey", "category_total": 24.0, "date": "Mar. 4, 2002"}
]}'''
