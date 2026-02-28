# -*- coding: utf-8 -*-
import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print('='*80)
print('Sync level from const to institutions')
print('='*80)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    print('\n[1] Check differences...')
    cursor.execute("""
        SELECT 
            i.id, i.name, i.level as curr, c.level as const_level
        FROM institutions i
        JOIN const_init_institutions c ON BINARY i.uscc = BINARY c.uscc
        WHERE BINARY i.level != BINARY c.level 
           OR (i.level IS NULL AND c.level IS NOT NULL)
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if rows:
        print(f'  Found {len(rows)} differences:')
        for r in rows:
            print(f'    ID={r[0]}, {r[1][:25]}, curr={r[2]}, const={r[3]}')
    
    print('\n[2] Count total...')
    cursor.execute("""
        SELECT COUNT(*)
        FROM institutions i
        JOIN const_init_institutions c ON BINARY i.uscc = BINARY c.uscc
        WHERE BINARY i.level != BINARY c.level 
           OR (i.level IS NULL AND c.level IS NOT NULL)
    """)
    total = cursor.fetchone()[0]
    print(f'  Total to update: {total}')
    
    if total == 0:
        print('\n  All synced!')
        conn.close()
        exit(0)
    
    print('\n[3] Updating...')
    cursor.execute("""
        UPDATE institutions i
        JOIN const_init_institutions c ON BINARY i.uscc = BINARY c.uscc
        SET i.level = c.level
        WHERE BINARY i.level != BINARY c.level 
           OR (i.level IS NULL AND c.level IS NOT NULL)
    """)
    updated = cursor.rowcount
    conn.commit()
    print(f'  Updated: {updated} records')
    
    print('\n[4] Sample after update...')
    cursor.execute('SELECT id, name, level FROM institutions LIMIT 5')
    samples = cursor.fetchall()
    for s in samples:
        print(f'    ID={s[0]}, {s[1][:30]}, level={s[2]}')
    
    print('\n' + '='*80)
    print(f'DONE! Updated {updated} records')
    print('='*80)

except Exception as e:
    print(f'\nError: {e}')
    conn.rollback()
finally:
    cursor.close()
    conn.close()
