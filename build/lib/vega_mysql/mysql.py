import pymysql
from sshtunnel import SSHTunnelForwarder


class MySQLError(Exception):
    #------------------------------------------------
    # 생성할 때 value 값을 입력 받은다.
    # -----------------------------------------------
    def __init__(self, value):
        self.value = value

    #------------------------------------------------
    # 생성할 때 받은 value 값을 확인 한다.
    # -----------------------------------------------
    def __str__(self):
        return self.value


# ---------------------------------------------------------------------------------------------------------------------------
#   [의존성]
#       - pip install PyMySQL
#       - pip install sshtunnel
#   [사용법]
#       from vega_mysql import MySQl
#
#       sql = MySQL(**kwargs)
#       sql.connect()
#       result = sql.fetchall(query)
#               :
#       sql.close()
#       또는
#       sql = MySQL(**kwargs)
#       conn = sql.connect()
#       cursor = conn.cursor('user define cursor')
#       cursor.execute(query, data)
#       result = cursor.fetchall()
#               :
#       sql.close()
#   [args]
#       host="ip 또는 dns"               --> 필수 입력값
#       user="user_id"                  --> 필수 입력값
#       passwd="user password"          --> 필수 입력값
#       database="database name"        --> 필수 입력값
#       port="port number"              --> Int value, default 3306
#       charset="character type"        --> default utf8
#       tunneling=True or False         --> default False
#       ssh_host="ip 또는 dns"           --> default None
#       ssh_user="tunneling user"       --> default None
#       ssh_key="key 값이 존재하는 파일"    --> default None
#       ssh_passwd="ssh_user의 passwd"  --> default None
#   [method]
#       - fetchone(query), fetchone_with(query, data)
#       - fetchall(query), fetchall_with(query, data)
#       - fetchmany(query), fetchmany_with(query, data)
#       - execute(query), execute_with(query, data)
#       - bulk(sql, lists)
#   [주의]
#       1. connect() 후 반드시 close()를 처리해야 한다.
#       2. tunneling이 True이면 반드시 ssh->passwd 또는 ssh->key 값에 둘 중 하나만 값이 존재하여야 한다.
#       3. defult cursor는 pymysql.cursors.DictCursor
#       4. 사용자가 cursor를 정의하고자 할 때
#           import pymysql
#           from vega_mysql import MySQL
#           sql = MySQL(**kwargs)
#           conn = sql.connect()
#           cursor = conn.cursor('user define cursor')
#           cursor.execute(query, data)
#           result = cursor.fetchall()
#                   :
#           sql.close()
# ---------------------------------------------------------------------------------------------------------------------------
class MySQL:
    def __init__(self, **kwargs):
        try:
            self.__cursor = None
            self.__tunnel = None
            self.__connect = None
            self.__ssh_host = kwargs.get('ssh_host', None)
            self.__ssh_port = kwargs.get('ssh_port', 22)
            self.__ssh_user = kwargs.get('ssh_user', None)
            self.__ssh_key = kwargs.get('ssh_key', None)
            self.__ssh_passwd = kwargs.get('ssh_passwd', None)
            self.__host = kwargs.get('host', None)
            self.__port = kwargs.get('port', 3306)
            self.__user = kwargs.get('user', None)
            self.__passwd = kwargs.get('passwd', None)
            self.__database = kwargs.get('database', None)
            self.__charset = kwargs.get('charset', 'utf8')
            self.__tunneling = kwargs.get('tunneling', False)
            # 필수입력값 체크
            if self.__host is None or self.__user is None or self.__passwd is None or self.__database is None:
                msg = '"host", "user", "passwd", "database" are required inputs.'
                raise MySQLError(msg)
            # 터널링 입력값 체크
            if self.__tunneling:
                if self.__ssh_host is None or self.__ssh_user is None:
                    msg = '"ssh_host", "ssh_user" are required inputs.'
                    raise MySQLError(msg)
                if self.__ssh_key is not None and self.__ssh_passwd is not None:
                    msg = 'Only one of the values of "ssh_key" and "ssh_passwd" must be declared.'
                    raise MySQLError(msg)
        except Exception as e:
            msg = 'Exception occured in __init__(). Message: %s' % str(e)
            raise MySQLError(msg)

    # ------------------------------------------------------------
    #   connect()
    # ------------------------------------------------------------
    def connect(self):
        try:
            # 접속방식이 Tunneling 설정되어 있으면
            if self.__tunneling:
                if self.__ssh_passwd is not None:
                    self.__tunnel = SSHTunnelForwarder(
                        (self.__ssh_host, self.__ssh_port),
                        ssh_username = self.__ssh_user,
                        ssh_password = self.__ssh_passwd,
                        remote_bind_address=(self.__host, self.__port)
                    )
                elif self.__ssh_key is not None:
                    self.__tunnel = SSHTunnelForwarder(
                        (self.__ssh_host, self.__ssh_port),
                        ssh_username = self.__ssh_user,
                        ssh_pkey = self.__ssh_key,
                        remote_bind_address=(self.__host, self.__port)
                    )
                # 터널링 시작
                self.__tunnel.start()
               # database connecttion
                self.__connect = pymysql.connect(
                    host = '127.0.0.1',
                    port=self.__tunnel.local_bind_port,
                    user = self.__user,
                    passwd = self.__passwd,
                    database = self.__database,
                    charset = self.__charset
                )
            else:
                # database connecttion
                self.__connect = pymysql.connect(
                    host=self.__host,
                    user=self.__user,
                    password=self.__passwd,
                    database=self.__database,
                    charset=self.__charset
                )
            self.__cursor = self.__connect.cursor(pymysql.cursors.DictCursor)
            return self.__connect
        except Exception as e:
            msg = 'Exception occured in connect(). Message: %s' % str(e)
            raise MySQLError(msg)

    # ------------------------------------------------------------
    #   close()
    # ------------------------------------------------------------
    def close(self):
        try:
            if self.__cursor is not None:
                self.__cursor.close()
                self.__cursor = None
            if self.__connect is not None:
                self.__connect.close()
                self.__connect = None
            if self.__tunnel is not None:
                self.__tunnel.close()
                self.__tunnel = None
        except Exception as e:
            msg = 'Exception occured in close(). Message: %s' % str(e)
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name;"
    #   result = conn.fetchall(query)
    # ------------------------------------------------------------
    def fetchone(self, query):
        try:
            self.__cursor.execute(query)
            return self.__cursor.fetchone()
        except Exception as e:
            # close database
            self.close()
            msg = 'Exception occured in fetchone(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name where id = %s;"
    #   data = ('jinland', )
    #   result = conn.fetchall(query, data)
    # ------------------------------------------------------------
    def fetchone_with(self, query, data):
        try:
            self.__cursor.execute(query, data)
            return self.__cursor.fetchone()
        except Exception as e:
            # close database
            self.close()
            msg = 'Exception occured in fetchone_with(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name;"
    #   result = conn.fetchall(query)
    # ------------------------------------------------------------
    def fetchall(self, query):
        try:
            self.__cursor.execute(query)
            return self.__cursor.fetchall()
        except Exception as e:
            # close database
            self.close()
            msg = 'Exception occured in fetchall(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name where id = %s;"
    #   data = ('jinland', )
    #   result = conn.fetchall(query, data)
    # ------------------------------------------------------------
    def fetchall_with(self, query, data):
        try:
            self.__cursor.execute(query, data)
            return self.__cursor.fetchall()
        except Exception as e:
            # close database
            self.close()
            msg = 'Exception occured in fetchall_with(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name;"
    #   result = conn.fetchall(query)
    # ------------------------------------------------------------
    def fetchmany(self, query):
        try:
            self.__cursor.execute(query)
            return self.__cursor.fetchmany()
        except Exception as e:
            # close database
            self.close()
            msg = 'Exception occured in fetchmany(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name where id = %s;"
    #   data = ('jinland', )
    #   result = conn.fetchall(query, data)
    # ------------------------------------------------------------
    def fetchmany_with(self, query, data):
        try:
            self.__cursor.execute(query, data)
            return self.__cursor.fetchmany()
        except Exception as e:
            # close database
            self.close()
            msg = 'Exception occured in fetchmany_with(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   insert delete update 구문에 대하여 적용
    #   query = "insert into table_name (column1, .....);"
    #   result = 성공 -> 1, 실패 -> 0
    # ------------------------------------------------------------
    def execute(self, query):
        try:
            result = self.__cursor.execute(query)
            self.__connect.commit()
            return result
        except Exception as e:
            self.close()
            msg = 'Exception occured in execute(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name where id = %s;"
    #   data = ('jinland', )
    #   result = conn.execute_with(query, data)
    # ------------------------------------------------------------
    def execute_with(self, query, data):
        try:
            result = self.__cursor.execute(query, data)
            self.__connect.commit()
            return result
        except Exception as e:
            self.close()
            msg = 'Exception occured in execute_with(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   insert delete update 구문에 대하여 적용
    #   query = "insert into table_name (column1, .....);"
    #   result = 성공 -> 1, 실패 -> 0
    # ------------------------------------------------------------
    def executeall(self, queries):
        try:
            for query in queries:
                result = self.__cursor.execute(query)
            self.__connect.commit()
            return result
        except Exception as e:
            self.__connect.rollback()
            self.close()
            msg = 'Exception occured in executeall(). query: %s,  Message: %s' % (queries, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   query = "select * from table_name where id = %s;"
    #   data = ('jinland', )
    #   result = conn.executeall_with(query, data)
    # ------------------------------------------------------------
    def executeall_with(self, queries, datas):
        try:
            result = 0
            if len(queries) == len(datas):
                idx = 0
                for query in queries:
                    result = self.__cursor.execute(query, datas[idx])
                    idx += 1
                self.__connect.commit()
            else:
                msg = 'The arrays are not the same size. queries: %s, datas: %s' % (len(queries), len(datas))
                raise MySQLError(msg)
            return result
        except Exception as e:
            self.__connect.rollback()
            self.close()
            msg = 'Exception occured in executeall_with(). query: %s,  Message: %s' % (queries, str(e))
            raise MySQLError(msg)

    # ------------------------------------------------------------
    # [사용법]
    #   대량의 데이타를 inseert 하고자 할 때 사용
    #   쿼리 전체가 모두 성공하면 리턴값은 True, 실패하면 rollback되고 False 리턴
    #   result = conn.bulk(query, datas)
    # ------------------------------------------------------------
    def bulk(self, query, datas):
        try:
            result = self.__cursor.executemany(query, datas)
            # commit
            self.__connect.commit()    # connection 시 autocommit=True일 경우는 사용하지 않아도 됨.
            return result
        except Exception as e:
            self.__connect.rollback()
            # close database
            self.close()
            msg = 'Exception occured in bulk(). query: %s,  Message: %s' % (query, str(e))
            raise MySQLError(msg)
