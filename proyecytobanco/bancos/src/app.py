from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'

# Rutas de la aplicación
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@app.route('/insert_cliente', methods=['POST'])
def insert_cliente():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    estado = request.form['estado']
    telefono = request.form['telefono']

    try:
        conn = db.connect()
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
        flash('Cliente creado correctamente')
    except Exception as e:
        flash(f'Error al crear el cliente: {e}')
    finally:
        cursor.close()
        conn.close()

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

    try:
        conn = db.connect()
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
        flash('Pago registrado correctamente')
    except Exception as e:
        flash(f'Error al registrar el pago: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('pagos'))

# Nueva ruta de búsqueda de clientes por DNI
@app.route('/buscar_cliente', methods=['POST'])
def buscar_cliente():
    dni = request.form['dniBuscar']
    conn = None
    cursor = None
    resultados = []
    try:
        conn = db.connect()
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
            flash('Cliente no encontrado.')
    except Exception as e:
        flash(f'Error al buscar el cliente: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template('clientes.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)
