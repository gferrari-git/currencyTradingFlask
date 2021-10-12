import sqlobject as SO
import os
import conf

if conf.db == 'mysql':
    database = 'mysql://trader_guest:trader_guest@localhost/trader'      
else:
    database = 'sqlite:/'+os.getcwd().replace('\\','/')+'/test.sqlite' 
    
__connection__=SO.connectionForURI(database)

class UserInfo(SO.SQLObject):

    """Clase que permite realizar la abstraccion con la tabla user_info
de la base de datos"""
    
    name=SO.StringCol(length=40)
    pwd =SO.StringCol(length=40)
    
class Account(SO.SQLObject):

    """Clase que permite realizar la abstraccion con la tabla account
de la base de datos"""
    
    currency=SO.StringCol(length=3)
    amount=SO.DecimalCol(size=8,precision=2)
    user=SO.ForeignKey('UserInfo', cascade=True)


class DataHelper:

    """Clase que permite realizar las operaciones de consulta
escritura y acyualizacion de la base de datos"""
    
    def getOneUser(self,params):
    
        """Metodo que busca un usuario identificado por su nombre en la base
de datos y lo devuelve si existe, de lo contrario devuelve False"""

        try:
            res=UserInfo.selectBy(name=params).getOne()
            return dict(name=res.name,pwd=res.pwd)
        except:
            return False
        
    def getAccounts(self,params,coin='ALL'):
    
        """Metodo que busca las cuentas de un usuario indentificado 
por su nombre en la base de datos y las devuelve como una lista si existen,
de lo contrario devuelve None"""

        try:
            id=UserInfo.selectBy(name=params).getOne().id
            res=[]
            if coin=='ALL':
                for account in Account.selectBy(user=id):
                    res.append(dict(currency=account.currency,amount=account.amount))
                return res
            else:
                for account in Account.selectBy(user=id,currency=coin):
                    res.append(dict(currency=account.currency,amount=account.amount))
                return res
        except:
            return None
    
    def setAmount(self,userName,currency,cnt):
    
        """Metodo que setea el monto indicado, en la cuenta de la moneda
indicada del usuario indicado. Devuelve True si tiene exito, False de 
lo contrario"""

        try:
            id=UserInfo.selectBy(name=userName).getOne().id
            res=Account.selectBy(user=id,currency=currency).getOne()
            res.amount=cnt
            return True
        except:
            return None
            
    def setAccount(self,userName,currency):
    
        """Metodo que guarda una nueva cuenta de la moneda
indicada perteneciente al usuario indicado Devuelve True 
si tiene exito, None si falla"""

        try:
            id=UserInfo.selectBy(name=userName).getOne().id
            Account(currency=currency,amount=0.0,user=id)
            return True
        except:
            return None
    
    def setUser(self,userName,pwd):
    
        """Metodo que guarda una nuevo usuario con su password ya encriptado.
Devuelve True si tiene exito, None si falla"""

        try:
            UserInfo(name=userName,pwd=pwd)
            return True
        except:
            return None
    
        
        
        