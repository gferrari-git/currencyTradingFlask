from business.admin import Admin,Buyer,Depositor,Collector,AccountBuilder,UserBuilder
from decimal import Decimal
import getpass
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Screens.login import Ui_Login
from Screens.principal import Ui_MainWindow
from Screens.createAccount import Ui_CrearDialog

class LoginDialog (QDialog,Ui_Login):
    def __init__(self,parent=None,nextDiag=None):
        super(LoginDialog, self).__init__(parent)
        self.admin=Admin()
        self.setupUi(self)
        self.diag=nextDiag
        self.btnOK.clicked.connect(self.btnlog) 
        self.btnCancel.clicked.connect(lambda:self.close())

    def btnlog(self):
        if self.admin.CheckValidate(self.UserEdit.text(),self.PassEdit.text()):
            self.UserEdit.setText('')
            self.PassEdit.setText('')
            self.diag.admin=self.admin
            result = self.admin.CheckAccount()
            if result is None:
                pass#usuario incorrecto
            elif result == False:
                print ('No hay cuentas')
            else:
                print ('Cuentas:')
                for count in result:
                    self.diag.countsList.addItem(count['currency'])

            self.diag.show()
            self.close()
        else:
            print ('Password y/o usuario Incorrecto')

class Principal (QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(Principal, self).__init__(parent)
        self.admin=None
        self.setupUi(self)
        self.CreateAccount.clicked.connect(self.btnCrear) 
        self.countsList.currentItemChanged.connect(lambda :self.showAmmount(self.countsList.currentItem().text()))
        
    def btnCrear(self):
        diag=CrearDialog(admin=self.admin)

        diag.exec_()
        self.countsList.clear()
        result = self.admin.CheckAccount()

        for count in result:
            self.countsList.addItem(count['currency'])
            

    def showAmmount(self,currency):
        print(currency)
        result=self.admin.CheckAccount()
        for count in result:
            if count['currency']==currency:
                self.label.setText(count['currency']+' '+str(count['amount']))

class CrearDialog (QDialog,Ui_CrearDialog):
    def __init__(self,parent=None,admin=None):
        super(CrearDialog, self).__init__(parent)
        self.admin=admin
        self.setupUi(self)
        for currency in admin.CurrencyQuery().keys():        
            self.countSelect.addItem(currency)
        self.btnOK.clicked.connect(lambda:self.CrearOK(self.countSelect.currentText()))
        self.btnCancel.clicked.connect(lambda:self.close())

    def CrearOK(self,crncy):
        print(crncy)
        MyAccountBuilder=AccountBuilder(crncy)
        res=MyAccountBuilder.prepare(self.admin)

        if res==False:
            print('La cuenta ya existe')
            self.close()
        elif res is None:
            print('La Moneda no existe')
            self.close()
        else:
            #confirmacion
            rv=MyAccountBuilder.Build(self.admin)
            if rv == True:
                print('Cuenta Creada con Exito!')
            else:
                print('Error')
            self.close()


class App(object):

    """Clase Base de la Aplicacion, usada para iniciarla"""
    
    def main():
        """Metodo que inicia la aplicacion y 
        realiza el bucle de seleccion de opciones"""
        app=QApplication([])
        logOk=Principal()
        window=LoginDialog(nextDiag=logOk)
        window.show()
        app.exec()
        print('pepe')
    
        #admin = Admin()
        #myLogger=Logger(admin)
        # loop = True
        # while loop==True:
        #     loop =myLogger.ShowMenu()
        # if myLogger.admin.userName != '':
        #     loop = True
        #     while loop ==True:
        #         loop=myLogger.ShowUserMenu()
        # else:
        #     print('Fallo el loggeo')

class Logger(object):

    """Clase Encargada de mostrar opciones en 
    la pantalla y mostrar resultados"""
    
    def __init__(self,admin):
        self.admin=admin

    def ShowLogin(self):

        """Metodo que toma los datos del login (user y pwd) e 
        informa la validacion del mismo"""
        
        name=input("User:")
        pwd = getpass.getpass('Password:')
        result = self.admin.CheckValidate(name, pwd)
        if result==True:
            print ('Acceso correcto')
        elif result == False:
            print ('Password y/o usuario Incorrecto')
        else:
            print ('Password y/o usuario Incorrecto')
            
    def ShowMenu(self):
    
        """Metodo que muestra el menu de Bienvenida y opciones iniciales (Login
        y crear usuario). Devuelve False si se eligio Login para dar 
        paso a ShowUserMenu y True si se eligio cualquier otra opcion, para forzar
        otro ciclo de main"""
    
        print('Bienvenido a la app de compra y venta de moneda')
        print('Ingrese la Opcion que desea Realizar:')
        print('1-Login','2-Crear Usuario',sep='\n')
        try:
            opt=int(input())
            if opt==1:
                self.ShowLogin()
                self.ShowAccounts()
                return False
            elif opt==2:
                myOpIfce=OpInterface(self.admin)
                myOpIfce.BuildUser() 
                return True
            else:
                print('Opcion Incorrecta')
                return True
        except:
            print('Opcion Incorrecta')
            return True

    def ShowUserMenu(self):
    
        """Metodo que muestra el menu de Usuario y opciones especificas
        (Comprar,depositar, crear cuenta).Devuelve True si realizo una 
        operacion con exito y False si se ingreso la opcion Salir"""

        myOpIfce=OpInterface(self.admin)
        print('Ingrese la Opcion que desea Realizar, cualquier otra para salir')
        print('1-Comprar','2-Depositar','3-Crear Cuenta',sep='\n')
        try:
            opt=int(input())
            if opt==1:
                myOpIfce.Buy() 
                self.ShowAccounts()
                return True
            elif opt==2:
                myOpIfce.Deposit() 
                self.ShowAccounts()
                return True   
            elif opt==3:
                myOpIfce.BuildAccount() 
                self.ShowAccounts()
                return True
            else:
                print('Adios')
                return False
        except:
            print('Adios')
            return False
            
    def ShowAccounts(self):
    
        """Metodo que muestra las cuentas y saldos del usuario loggeado"""
        
        result = self.admin.CheckAccount()
        if result is None:
            pass#usuario incorrecto
        elif result == False:
            print ('No hay cuentas')
        else:
            print ('Cuentas:')
            for count in result:
                print('Moneda-> '+count['currency']+\
                ' Saldo-> {:.2f}'.format(count['amount']))
                
class OpInterface(object):

    """Clase que opera como interfaz de Usuario para las 
    operaciones compra, deposito, creacion de usuarios y cuentas
    Para usar sus metodos el usuario debe estar correctamente loggeado
    excepto por BuildUser"""
    
    def __init__(self,admin):
        self.admin=admin
        
    def Buy(self):
    
        """Metodo que funciona como interfaz de usuario para la compra o
        intrecambio de moneda. Toma los datos moneda origen, destino, 
        cantidad a comprar o a debitar e informa sobre el resultado de la
        operacion"""
        
        org=input('Moneda Origen:').upper()
        dst=input('Moneda Destino:').upper()
        op=input("1-Cantidad a comprar\n2-Cantidad a debitar:\n")
        if op=='1':
            op='BUY'
        elif op=='2':
            op='DEBIT'
        else:
            print('Opcion Incorrecta')
            return
        cnt=Decimal(input('Cantidad:'))
        MyBuyer=Buyer(operation=op,org=org,dst=dst,cnt=cnt)
        res=MyBuyer.prepare(self.admin)
        if res != False:
        
            if res['status']=='OK':
            
                print('Saldo Suficiente, Su balance sera {:.2f} {} y {:.2f} {}'
                    .format(res['bal_org'],org,res['bal_dst'],dst))
                    
                ack=input('Desea Comfirmar?(S/N):\n')
                if ack.lower()=='s':
                    if (MyBuyer.validate(self.admin,
                        res['bal_org'],res['bal_dst'])) == True:
                        
                        print('Compra Exitosa!')
                        
                    else:
                        print('Error')
                else:
                    print('Cancelado')
                    
            elif res['status']=='NOT OK': 
            
                print('Saldo Insuficiente, Su balance sera {:.2f} {} y {:.2f} {}'
                    .format(res['bal_org'],org,res['bal_dst'],dst))
                    
                return
                
            else:
                return
        else:
            print('No existe la cuenta origen y/o destino, creela primero')
            return
           
    def Deposit(self):
            
        """Metodo que funciona como interfaz de usuario para el deposito de ARS.
        Toma los datos de cantidad de ARS y llama al metodo de cobro e informa 
        el resultado de la operacion"""
        
        cnt=Decimal(input('Ingrese la Cantidad de ARS a depositar:\n'))
        MyDepositor=Depositor(cnt)
        MyCollector=Collector()
        res=MyDepositor.prepare(self.admin)
        
        print('Luego del deposito su Saldo sera: {:.2f} ARS'.format(res))
        ack=input('Desea Comfirmar?(S/N):\n')
        
        if ack.lower()=='s':
            rv=MyDepositor.validate(self.admin)
            rv2=MyCollector.validate() #aqui realizaria el cobro
            if (rv and rv2) == True:
                print('Deposito Exitoso!')
            else:
                print('Error')
        else:
            print('Cancelado')

    def BuildAccount(self):
    
        """Metodo que funciona como interfaz de usuario para la creacion de cuenta.
        Toma los datos de la moneda de cuenta e informa el resultado de la operacion"""

        crncy=input('Ingrese la Moneda de la Cuenta a Crear:\n')
        MyAccountBuilder=AccountBuilder(crncy)
        res=MyAccountBuilder.prepare(self.admin)
        if res==False:
            print('La cuenta ya existe')
            return
        elif res is None:
            print('La Moneda no existe')
            return
        else:
            ack=input(
            'Desea Crear una nueva Cuenta en {}?(S/N):\n'.format(crncy.upper()))
            if ack.lower()=='s':
                rv=MyAccountBuilder.Build(self.admin)
                if rv == True:
                    print('Cuenta Creada con Exito!')
                else:
                    print('Error')
            else:
                print('Cancelado')
            
    def BuildUser(self):
    
        """Metodo que funciona como interfaz de usuario para la creacion de Usuario.
        Toma los datos usuario y password e informa el resultado de la operacion"""

        name=input('Ingrese el nombre Usuario a Crear:\n')
        pwd=input('Ingrese la clave de Acceso:\n')
        MyUserBuilder=UserBuilder(name,pwd)
        rv=MyUserBuilder.validateUser(self.admin)
        if rv==False:
            print('El ususario ya Existe')
            return
        else:
            pwd=input('Ingrese Nuevamente la clave de Acceso:\n')
            rv=MyUserBuilder.validatePwd(pwd)
            if rv== False:
                print('Las claves no coinciden')
                return
            else:
                ack=input('Comfirma la creacion de Usuario?(S/N):\n')
                if ack.lower()=='s':
                    rv=MyUserBuilder.Build(self.admin)
                    if rv==False:
                        print('Error')
                        return
                    else:
                        print('Usuario Creado con exito')
                        return
                else:
                    print('Cancelado')
                    return
    
             