from handy.connections import ChinaCursor


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

    return test_data
