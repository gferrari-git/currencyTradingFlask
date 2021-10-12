# CurrencyTrade

CurrencyTrade es una App de Python para Compra y Venta de Divisas.

## Instalacion

1-Clonar este repositorio

2-Crear un entorno virtual dentro del mismo

python -m venv Nombre_del_entorno

3-Activar el entorno virtual

Windows:

Nombre_del_entorno/Scripts/activate.bat

Linux:

source Nombre_del_entorno/bin/activate


4-Instalar Dependencias dentro del entorno

pip install -r dependencies.txt


5-Se debe tener instalado un servidor de MySQL o de SQLite

En el caso de MySQL debe cargarse los datos de la db como root (Esto crea la base de datos, el usuario de conexion y las tablas)

mysql -u root -p < Path_Al_Repo_Local/test.sql

## Uso
Con el entorno virtual activado

python main.py 

Por defecto, la app viene configurada para usar sqlite, para usar MySql se debe editar el archivo conf,py
y cambiar

db='sqlite'

Por

db='mysql'

Por defecto hay un usuario creado cuyo nombre es test y su clave es tambien test

Cuando se finaliza de usar desactivar el entorno virtual

Windows:

Nombre_del_entorno/Scripts/deactivate


Linux:

deactivate

