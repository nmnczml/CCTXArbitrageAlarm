from pymysqlpool.pool import Pool

m_host = 'yourDBIpOrDNS'
m_port = 12345
m_user = 'yourDBUser'
m_password = 'yourDBPassWord'
m_db = 'yourDBSchema'

def getPool():
    pool = Pool(host=m_host,
                port=m_port,
                user=m_user, password=m_password, db=m_db,
                min_size=20, max_size=30,timeout=20,autocommit=True)
    
    return pool