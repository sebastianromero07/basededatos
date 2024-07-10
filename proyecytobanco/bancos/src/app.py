from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import database as db
from werkzeug.security import generate_password_hash, check_password_hash

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'

# Rutas de la aplicación
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@app.route('/register', methods=['POST'])
def register():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    password = request.form['password']
    tipo_empleado = request.form['tipo_empleado']
    sueldo = 1500  # Sueldo por defecto para todos los empleados

    hashed_password = generate_password_hash(password)  # Utiliza el método de hash por defecto

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Insertar en la tabla persona
        query_persona = '''
            INSERT INTO persona (dni, nombre, apellido, direccion)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query_persona, (dni, nombre, apellido, direccion))

        # Insertar en la tabla empleado
        query_empleado = '''
            INSERT INTO empleado (persona_dni, sueldo)
            VALUES (%s, %s)
        '''
        cursor.execute(query_empleado, (dni, sueldo))

        # Insertar en la tabla específica del tipo de empleado
        if tipo_empleado == 'analista':
            query_tipo = '''
                INSERT INTO analista (persona_dni, sueldo)
                VALUES (%s, %s)
            '''
        elif tipo_empleado == 'cajero':
            query_tipo = '''
                INSERT INTO cajero (persona_dni, sueldo)
                VALUES (%s, %s)
            '''
        elif tipo_empleado == 'comite':
            query_tipo = '''
                INSERT INTO comite (persona_dni, sueldo)
                VALUES (%s, %s)
            '''
        cursor.execute(query_tipo, (dni, sueldo))

        # Insertar la contraseña en una tabla de autenticación
        query_auth = '''
            INSERT INTO autenticacion (persona_dni, password)
            VALUES (%s, %s)
        '''
        cursor.execute(query_auth, (dni, hashed_password))

        conn.commit()
        flash('Empleado registrado correctamente', 'success')

        # Crear una sesión para el usuario registrado
        session['user'] = dni

    except Exception as e:
        conn.rollback()
        flash(f'Error al registrar el empleado: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            db.release_connection(conn)

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    dni = request.form['dni']
    password = request.form['password']

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        query_auth = '''
            SELECT password FROM autenticacion WHERE persona_dni = %s
        '''
        cursor.execute(query_auth, (dni,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
            session['user'] = dni
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('DNI o contraseña incorrectos', 'danger')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error al iniciar sesión: {e}', 'danger')
        return redirect(url_for('home'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            db.release_connection(conn)

@app.route('/index')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        flash('Por favor, inicie sesión primero', 'warning')
        return redirect(url_for('home'))

@app.route('/insert_cliente', methods=['POST'])
def insert_cliente():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    estado = request.form['estado']
    telefono = request.form['telefono']

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        query_persona = '''
            INSERT INTO persona (dni, nombre, apellido, direccion)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query_persona, (dni, nombre, apellido, direccion))
        query_cliente = '''
            INSERT INTO cliente (persona_dni, estado, telefono)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(query_cliente, (dni, estado, telefono))
        conn.commit()
        flash('Cliente creado correctamente', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al crear el cliente: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            db.release_connection(conn)

    return redirect(url_for('clientes'))

@app.route('/pagos')
def pagos():
    return render_template('pagos.html')

@app.route('/insert_pago', methods=['POST'])
def insert_pago():
    dni = request.form['dni']
    cuotapago_idP = request.form['cuotapago_idP']
    mora = request.form['mora']
    fechapago = request.form['fechapago']
    montop = request.form['montop']

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        query_cuotapago = '''
            INSERT INTO cuotaPago (idP, mora, fechapago, montop)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query_cuotapago, (cuotapago_idP, mora, fechapago, montop))
        query_pagar = '''
            INSERT INTO pagar (persona_dni, cuotapago_idP)
            VALUES (%s, %s)
        '''
        cursor.execute(query_pagar, (dni, cuotapago_idP))
        conn.commit()
        flash('Pago registrado correctamente', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al registrar el pago: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            db.release_connection(conn)

    return redirect(url_for('pagos'))

# Nueva ruta de búsqueda de clientes por DNI
@app.route('/buscar_cliente', methods=['POST'])
def buscar_cliente():
    dni = request.form['dniBuscar']
    conn = None
    cursor = None
    resultados = []
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT p.dni, p.nombre, p.apellido, p.direccion, c.estado, c.telefono
            FROM persona p
            JOIN cliente c ON p.dni = c.persona_dni
            WHERE p.dni = %s
        '''
        cursor.execute(query, (dni,))
        resultados = cursor.fetchall()
        if not resultados:
            flash('Cliente no encontrado.', 'warning')
    except Exception as e:
        flash(f'Error al buscar el cliente: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            db.release_connection(conn)
    return render_template('clientes.html', resultados=resultados)

@app.route('/insert_prestamo', methods=['POST'])
def insert_prestamo():
    id = request.form['id']
    dni = request.form['dniPrestamo']
    ncuotas = request.form['ncuotas']
    fechaprestamo = request.form['fechaprestamo']
    importe = request.form['importe']
    interes = request.form['interes']
    a_persona_dni = request.form.get('a_persona_dni')  # DNI del analista

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Verificar si el cliente existe
        query_check_cliente = 'SELECT dni FROM persona WHERE dni = %s'
        cursor.execute(query_check_cliente, (dni,))
        cliente = cursor.fetchone()

        if not cliente:
            flash('Cliente no encontrado.', 'warning')
            return redirect(url_for('home'))

        # Insertar el préstamo
        query_prestamo = '''
            INSERT INTO prestamo (id, persona_dni, ncuotas, fechaprestamo, importe, interes, a_persona_dni)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query_prestamo, (id, dni, ncuotas, fechaprestamo, importe, interes, a_persona_dni))
        conn.commit()
        flash('Préstamo registrado correctamente', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al registrar el préstamo: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            db.release_connection(conn)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
