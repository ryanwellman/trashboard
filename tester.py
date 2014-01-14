from handy.connections import ChinaCursor
from json import loads


def Tester():
    cur = ChinaCursor()
    cur.SetCrossServerFlags()
    sql = '''
        SELECT [agreement_id], [blob]
        FROM contract_details
        WHERE agreement_id = '1478036'
    '''
    cur.execute(sql)
    test_data = cur.fetch_all()

    loaded = loads(test_data[0]['blob'])

    return loaded
