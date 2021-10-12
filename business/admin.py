from data.data_helper import DataHelper
import requests
from decimal import *
import bcrypt


class Admin(object):

    """Clase que funciona como interfaz entre capas de aplicacion
Contiene una instancia de DataHelper para acceder a la capa de datos
y el nombre del usuario loggeado"""
    
    def __init__(self):
        self.helper = DataHelper()
        ctx = Context(prec=10, rounding=ROUND_HALF_UP)
        setcontext(ctx) #seteo de presicion en los calculos decimales
              
    def CheckValidate(self,name,pwd):
    
        """Metodo que Chequea la validacion de user->pwd, 
pidiendo a la capa de datos los registros guardados.
Encripta pwd y lo compara con los registros
para validar o no el loggeo. Retorna True si el loggeo es valido,
False si el pwd es incorrecto y None si no existe el ususario"""
        
        pwd=pwd.encode('utf-8')
        res=self.helper.getOneUser(name)
        if res:
        
            if  bcrypt.hashpw(pwd, res['pwd']
                .encode('utf-8')) == res['pwd'].encode('utf-8'):
                
                self.userName=res['name']
                return True
                
            else:
            
                self.userName=''
                return False
        else:
            self.userName=''
            return None       

    def CheckAccount(self):
    
        """Metodo que Chequea que el usuario loggeado tenga cuentas creadas y si
es asi devuelve una lista con las mismas, Devuelve False si el usuario
no tiene cuentas y None si no existe el usuario"""
       
        if self.userName != '':
            res=self.helper.getAccounts(self.userName)
            if res != None:
                if res == []:
                    return False
                else:
                    return res
            else:
                return None            
    
    def ServiceQuery(self,org,dst):
    
        """Metodo que realiza una peticion al sitio fixer.io sobre la
cotizacion de las divisas, como se usa la version gratuita la divisa base
de la peticion sera EUR, por lo que consulta 2 cotizaciones (org y dst).
Devuelve False si alguna divisa de la peticion no existe, sino devuelve
la cotizacion de la divisa dst respecto de la divisa org"""
        

        res=requests.get("http://data.fixer.io/api/latest?access_key=8694056806013f8123e3ec7c9569ce1c&symbols={},{}".format(dst,org))
        try:
            dst_rate=res.json()['rates'][dst] #de euro a dst
            org_rate=res.json()['rates'][org] #de euro a org
        except KeyError:
            return False
        return (Decimal(org_rate)/Decimal(dst_rate))

    def CurrencyQuery(self):
        res=requests.get("http://data.fixer.io/api/symbols?access_key=8694056806013f8123e3ec7c9569ce1c")
        return res.json()['symbols']

class TradeManager(object):
    """Interfaz para clases de administracion de operaciones de compra/deposito"""
    def prepare(self):
        pass
    
    def validate(self):
        pass

class Builder(object):
    """Interfaz para clases de administracion de operaciones de creacion"""
    def Build(self):
        pass

class Buyer(TradeManager):

    """Clase que permite realizar compras de moneda, posee 
informacion sobre la moneda origen, destino, cantidad y si es 
cantidad a comprar o debitar """ 

    def __init__(self,operation,org,dst,cnt):
        self.operation=operation
        self.org=org
        self.dst=dst
        self.cnt=cnt
            
    def prepare(self,admin):
    
        """Metodo que realiza la preparacion de la operacion de compra
chequeando que existan las cuentas origen y destino y que el saldo sea
suficiente. Retorna False si no existe alguna de las cuentas. Si las cuentas
existen devuelve el estado de la transaccion mediante un diccionario
En la key status pondra 'OK' si el saldo es suficiente y 'NOT OK' si
no lo es"""

        res=admin.helper.getAccounts(admin.userName,self.dst)
        if res != None:
            if res == []:
                return False
            else:
                resdst = res[0]
                res=admin.helper.getAccounts(admin.userName,self.org)
                if res==[]:
                    return False
                resorg=res[0]
            rate=admin.ServiceQuery(self.org,self.dst)
            if self.operation=='BUY':
                if resorg['amount']>=self.cnt*rate:
                    return dict(status='OK',
                        bal_dst=resdst['amount']+self.cnt,
                        bal_org=(resorg['amount']-self.cnt*rate))
                else:
                    return dict(status='NOT OK',
                        bal_dst=resdst['amount']+self.cnt,
                        bal_org=(resorg['amount']-self.cnt*rate))
            elif self.operation=='DEBIT':
                if resorg['amount']>=self.cnt:
                    return dict(status='OK',
                        bal_dst=resdst['amount']+self.cnt/rate,
                        bal_org=(resorg['amount']-self.cnt))
                else:
                    return dict(status='NOT OK',
                        bal_dst=resdst['amount']+self.cnt/rate,
                        bal_org=(resorg['amount']-self.cnt))
            else:
                return None#operacion invalida  
        else:
            return False#No hay cuenta destino

    
    def validate(self,admin,bal_org,bal_dst):
    
        """Metodo que realiza la validacion de la operacion de compra
pidiendo a la capa de datos que almacene los nuevos estados de cuenta
devuelve True si tuvo exito, de lo contrario False"""

        rv=admin.helper.setAmount(admin.userName,self.org,bal_org)
        if rv!= None:
            rv=admin.helper.setAmount(admin.userName,self.dst,bal_dst)
            if rv != None:
                return True
            else:
                return False

class Depositor(TradeManager):

    """Clase que permite realizar depositos de ARS, posee
informacion sobre la cantidad a depositar """ 

    def __init__(self,cnt):
        self.cnt=cnt
        
    def prepare(self,admin):
    
        """Metodo que realiza la preparacion de la operacion de deposito
chequeando que existan la cuenta en ARS.
Retorna False si no existe alguna de las cuentas. Si las cuentas
existen devuelve True"""

        res=admin.helper.getAccounts(admin.userName,'ARS')
        if res is None:
            return False
        else:
            res=res[0]
            self.actual=res['amount']
            return (self.actual+self.cnt)
            
    def validate(self,admin):

        """Metodo que realiza la validacion de la operacion de deposito
pidiendo a la capa de datos que almacene el nuevo estado de cuenta
devuelve True si tuvo exito, de lo contrario False"""

        rv=admin.helper.setAmount(admin.userName,
            'ARS',self.actual+self.cnt)
        if rv is None:
            return False
        else:
            return True
            
class Collector(TradeManager):
    """Clase para realizacion de cobros, por ahora dejada en blanco"""
    def validate(self):
        return True

class AccountBuilder(Builder):

    """Clase para construccion de cuentas"""
    
    def __init__(self,currency):
        self.currency=currency.upper()
        
    def prepare(self,admin):

        """Metodo que realiza la preparacion de la operacion de creacion
de cuenta, chequeando que la cuenta no exista actualmente y la moenda elegida exista.
Retorna False si la cuenta ya existe, None si no existe la moneda elegida. 
True si todo esta OK
"""

        res=admin.helper.getAccounts(admin.userName,coin=self.currency)
        if res == []:
            x=admin.ServiceQuery('ARS',self.currency)
            if x!=False:
                return True
            else:
                return None
        else:
            return False
            
    def Build(self,admin):
    
        """Metodo que realiza la validacion de la operacion de creacion de cuenta
pidiendo a la capa de datos que almacene la nueva cuenta.
devuelve True si tuvo exito, de lo contrario False"""
    
        rv=admin.helper.setAccount(admin.userName,self.currency)
        if rv is None:
            return False
        else:
            return True

class UserBuilder(Builder):

    """Clase para construccion de Usuarios"""
    
    def __init__(self,name,pwd):
        self.name=name
        self.pwd=pwd
        
    def validateUser(self,admin):
    
        """Metodo que realiza la preparacion de la operacion de creacion
de usuario, chequeando que el usuario no exista actualmente. Devuelve True si no
existe y False si ya existe"""
    
        res=admin.helper.getOneUser(self.name)
        if res == False:
            return True
        else:
            return False
        
    def validatePwd(self,pwd2):

        """Metodo que realiza la preparacion de la operacion de creacion
de usuario, chequeando que el pwd ingresado sea valido por doble entrada.
Encripta el password y devuelve True si tiene exito o False si no valida el
password"""

        if self.pwd==pwd2:
            self.__encryptPwd = bcrypt.hashpw(self.pwd.encode('utf-8'),
                bcrypt.gensalt())
            return True
        else:
            return False
    
    def Build(self,admin):
    
        """Metodo que realiza la validacion de la operacion de creacion de usuario
pidiendo a la capa de datos que almacene lel nuevo usuario y su password encriptado.
Ademas crea una cuenta en ARS con saldo 0.00 correspondiente a dicho ususario.
Devuelve True si tuvo exito, de lo contrario False"""    

        rv=admin.helper.setUser(self.name,self.__encryptPwd.decode())
        if rv is None:
            return False
        else:
            rv=admin.helper.setAccount(self.name,'ARS')
            if rv is None:
                return False
            else:
                return True

            
            
            
            
            