import tkinter as tk
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Conexión a la base de datos
conn = sqlite3.connect("clientes.db")
c = conn.cursor()

# Crear tabla si no existe (con campo fecha_ingreso)
c.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    telefono TEXT,
    direccion TEXT,
    marca TEXT,
    modelo TEXT,
    falla TEXT,
    observacion TEXT,
    fecha_ingreso TEXT
)
""")
conn.commit()

# Funciones

def ingresar_cliente():
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datos = (
        nombre.get(), telefono.get(), direccion.get(), marca.get(),
        modelo.get(), falla.get(), observacion.get("1.0", tk.END).strip(),
        fecha
    )
    c.execute("""
        INSERT INTO clientes 
        (nombre, telefono, direccion, marca, modelo, falla, observacion, fecha_ingreso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    estado.config(text="Cliente ingresado con éxito", fg="green")
    limpiar_campos()

def buscar_cliente():
    criterio = nombre.get() or telefono.get() or direccion.get()
    c.execute("""
        SELECT * FROM clientes 
        WHERE nombre=? OR telefono=? OR direccion=?
    """, (criterio, criterio, criterio))
    cliente = c.fetchone()
    if cliente:
        nombre.set(cliente[1])
        telefono.set(cliente[2])
        direccion.set(cliente[3])
        marca.set(cliente[4])
        modelo.set(cliente[5])
        falla.set(cliente[6])
        observacion.delete("1.0", tk.END)
        observacion.insert(tk.END, cliente[7])
        fecha_ingreso.set(cliente[8])
        estado.config(text="Cliente encontrado", fg="blue")
    else:
        estado.config(text="Cliente no encontrado", fg="red")

def modificar_cliente():
    criterio = nombre.get() or telefono.get() or direccion.get()
    c.execute("SELECT * FROM clientes WHERE nombre=? OR telefono=? OR direccion=?", 
              (criterio, criterio, criterio))
    cliente = c.fetchone()

    if cliente:
        nuevo_nombre = nombre.get() or cliente[1]
        nuevo_telefono = telefono.get() or cliente[2]
        nuevo_direccion = direccion.get() or cliente[3]
        nuevo_marca = marca.get() or cliente[4]
        nuevo_modelo = modelo.get() or cliente[5]
        nuevo_falla = falla.get() or cliente[6]
        nuevo_observacion = observacion.get("1.0", tk.END).strip() or cliente[7]

        c.execute("""
            UPDATE clientes 
            SET nombre=?, telefono=?, direccion=?, marca=?, modelo=?, falla=?, observacion=?
            WHERE id=?
        """, (nuevo_nombre, nuevo_telefono, nuevo_direccion, nuevo_marca, nuevo_modelo, nuevo_falla, nuevo_observacion, cliente[0]))
        conn.commit()
        estado.config(text="Cliente modificado con éxito", fg="green")
        limpiar_campos()
    else:
        estado.config(text="Cliente no encontrado para modificar", fg="red")

def limpiar_campos():
    for var in [nombre, telefono, direccion, marca, modelo, falla, fecha_ingreso]:
        var.set("")
    observacion.delete("1.0", tk.END)
    estado.config(text="")

def exportar_a_pdf():
    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()

    if not clientes:
        estado.config(text="No hay clientes para exportar", fg="red")
        return

    archivo_pdf = "clientes_yangq2025.pdf"
    pdf = canvas.Canvas(archivo_pdf, pagesize=letter)
    ancho, alto = letter

    pdf.setFont("Helvetica-Bold", 14)
    y = alto - 50
    pdf.drawCentredString(ancho / 2, y, "Base de Datos de Clientes - YangQ2025")
    y -= 40

    pdf.setFont("Helvetica", 10)

    for cliente in clientes:
        texto = (
            f"Nombre: {cliente[1]} | Teléfono: {cliente[2]} | Dirección: {cliente[3]}",
            f"Marca: {cliente[4]} | Modelo: {cliente[5]} | Falla: {cliente[6]}",
            f"Observación: {cliente[7]}",
            f"Fecha Ingreso: {cliente[8]}"
        )
        for linea in texto:
            pdf.drawString(40, y, linea)
            y -= 15
            if y < 60:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = alto - 50
        y -= 10  # espacio entre clientes

    pdf.save()
    estado.config(text=f"PDF generado: {archivo_pdf}", fg="green")

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Base de Datos para Clientes YangQ2025")
ventana.geometry("520x650")

# Variables
nombre = tk.StringVar()
telefono = tk.StringVar()
direccion = tk.StringVar()
marca = tk.StringVar()
modelo = tk.StringVar()
falla = tk.StringVar()
fecha_ingreso = tk.StringVar()

# Campos
tk.Label(ventana, text="Nombre:").pack()
tk.Entry(ventana, textvariable=nombre).pack()

tk.Label(ventana, text="Teléfono:").pack()
tk.Entry(ventana, textvariable=telefono).pack()

tk.Label(ventana, text="Dirección:").pack()
tk.Entry(ventana, textvariable=direccion).pack()

tk.Label(ventana, text="Marca del equipo:").pack()
tk.Entry(ventana, textvariable=marca).pack()

tk.Label(ventana, text="Modelo:").pack()
tk.Entry(ventana, textvariable=modelo).pack()

tk.Label(ventana, text="Falla:").pack()
tk.Entry(ventana, textvariable=falla).pack()

tk.Label(ventana, text="Observación:").pack()
observacion = tk.Text(ventana, height=4)
observacion.pack()

tk.Label(ventana, text="Fecha de Ingreso:").pack()
tk.Entry(ventana, textvariable=fecha_ingreso, state="readonly").pack()

# Frame para botones con grid
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

# Botones (2 por fila)
btn_ingresar = tk.Button(frame_botones, text="Ingresar Cliente", width=20, command=ingresar_cliente)
btn_buscar = tk.Button(frame_botones, text="Buscar Cliente", width=20, command=buscar_cliente)
btn_modificar = tk.Button(frame_botones, text="Modificar Cliente", width=20, command=modificar_cliente)
btn_limpiar = tk.Button(frame_botones, text="Limpiar Campos", width=20, command=limpiar_campos)
btn_exportar = tk.Button(frame_botones, text="Exportar a PDF", width=20, command=exportar_a_pdf)

# Ubicar botones en grid: 2 por fila
btn_ingresar.grid(row=0, column=0, padx=5, pady=5)
btn_buscar.grid(row=0, column=1, padx=5, pady=5)
btn_modificar.grid(row=1, column=0, padx=5, pady=5)
btn_limpiar.grid(row=1, column=1, padx=5, pady=5)
btn_exportar.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Estado
estado = tk.Label(ventana, text="", font=("Arial", 12))
estado.pack(pady=10)

ventana.mainloop()
