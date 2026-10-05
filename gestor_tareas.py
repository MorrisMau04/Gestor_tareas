"""
Gestor de Tareas - Aplicación de Escritorio
Universidad Tecnológica de Puebla
Materia: Aplicaciones Web Progresivas

Aplicación de escritorio de ejemplo desarrollada en Python con Tkinter.
Permite agregar, completar, editar prioridad y eliminar tareas, con
persistencia local en un archivo JSON (sin necesidad de conexión a
internet ni de un navegador para funcionar).
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tareas.json")


class Tarea:
    def __init__(self, texto, prioridad="Media", completada=False, fecha=None):
        self.texto = texto
        self.prioridad = prioridad
        self.completada = completada
        self.fecha = fecha or datetime.now().strftime("%d/%m/%Y %H:%M")

    def to_dict(self):
        return {
            "texto": self.texto,
            "prioridad": self.prioridad,
            "completada": self.completada,
            "fecha": self.fecha,
        }

    @staticmethod
    def from_dict(d):
        return Tarea(d["texto"], d.get("prioridad", "Media"), d.get("completada", False), d.get("fecha"))


class GestorTareasApp:
    COLORES_PRIORIDAD = {"Alta": "#e74c3c", "Media": "#f39c12", "Baja": "#27ae60"}

    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tareas - Aplicación de Escritorio")
        self.root.geometry("560x520")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.tareas = []
        self.cargar_tareas()

        self._construir_interfaz()
        self._refrescar_lista()

    # ---------- Persistencia local (característica clave de app de escritorio) ----------
    def cargar_tareas(self):
        if os.path.exists(ARCHIVO_DATOS):
            try:
                with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.tareas = [Tarea.from_dict(d) for d in datos]
            except (json.JSONDecodeError, OSError):
                self.tareas = []
        else:
            self.tareas = [
                Tarea("Instalar entorno de Aplicaciones Web Progresivas", "Alta", False),
                Tarea("Leer documentación de Service Workers", "Media", False),
                Tarea("Entregar reporte de aplicación de escritorio", "Alta", False),
            ]
            self.guardar_tareas()

    def guardar_tareas(self):
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tareas], f, ensure_ascii=False, indent=2)

    # ---------- Interfaz gráfica nativa (Tkinter / Tk, widgets del sistema operativo) ----------
    def _construir_interfaz(self):
        titulo = tk.Label(
            self.root, text="Gestor de Tareas", font=("Segoe UI", 18, "bold"),
            bg="#1e1e2e", fg="#cdd6f4"
        )
        titulo.pack(pady=(15, 5))

        subtitulo = tk.Label(
            self.root, text="Aplicación de escritorio · funciona sin conexión a internet",
            font=("Segoe UI", 9), bg="#1e1e2e", fg="#a6adc8"
        )
        subtitulo.pack(pady=(0, 10))

        frame_entrada = tk.Frame(self.root, bg="#1e1e2e")
        frame_entrada.pack(pady=5, padx=20, fill="x")

        self.entrada_texto = tk.Entry(frame_entrada, font=("Segoe UI", 11), width=28)
        self.entrada_texto.grid(row=0, column=0, padx=(0, 5), ipady=4)
        self.entrada_texto.bind("<Return>", lambda e: self._agregar_tarea())

        self.combo_prioridad = ttk.Combobox(
            frame_entrada, values=["Alta", "Media", "Baja"], width=8, state="readonly"
        )
        self.combo_prioridad.set("Media")
        self.combo_prioridad.grid(row=0, column=1, padx=5)

        btn_agregar = tk.Button(
            frame_entrada, text="Agregar", command=self._agregar_tarea,
            bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=10, cursor="hand2"
        )
        btn_agregar.grid(row=0, column=2, padx=(5, 0))

        # Lista de tareas
        frame_lista = tk.Frame(self.root, bg="#1e1e2e")
        frame_lista.pack(pady=10, padx=20, fill="both", expand=True)

        self.canvas_lista = tk.Canvas(frame_lista, bg="#181825", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.canvas_lista.yview)
        self.frame_interno = tk.Frame(self.canvas_lista, bg="#181825")

        self.frame_interno.bind(
            "<Configure>", lambda e: self.canvas_lista.configure(scrollregion=self.canvas_lista.bbox("all"))
        )
        self.canvas_lista.create_window((0, 0), window=self.frame_interno, anchor="nw", width=500)
        self.canvas_lista.configure(yscrollcommand=scrollbar.set)

        self.canvas_lista.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Barra de estado
        self.label_estado = tk.Label(
            self.root, text="", font=("Segoe UI", 9), bg="#1e1e2e", fg="#a6adc8"
        )
        self.label_estado.pack(pady=(0, 10))

    def _refrescar_lista(self):
        for widget in self.frame_interno.winfo_children():
            widget.destroy()

        if not self.tareas:
            tk.Label(
                self.frame_interno, text="No hay tareas. ¡Agrega una arriba!",
                bg="#181825", fg="#6c7086", font=("Segoe UI", 10, "italic")
            ).pack(pady=20)

        for idx, tarea in enumerate(self.tareas):
            fila = tk.Frame(self.frame_interno, bg="#181825", pady=4)
            fila.pack(fill="x", padx=8, pady=2)

            var = tk.BooleanVar(value=tarea.completada)
            chk = tk.Checkbutton(
                fila, variable=var, bg="#181825", activebackground="#181825",
                command=lambda i=idx, v=var: self._marcar_completada(i, v.get())
            )
            chk.grid(row=0, column=0, rowspan=2, padx=(0, 8))

            fuente_tachado = ("Segoe UI", 11, "overstrike") if tarea.completada else ("Segoe UI", 11)
            color_texto = "#6c7086" if tarea.completada else "#cdd6f4"
            tk.Label(
                fila, text=tarea.texto, font=fuente_tachado, bg="#181825",
                fg=color_texto, anchor="w", wraplength=300, justify="left"
            ).grid(row=0, column=1, sticky="w")

            tk.Label(
                fila, text=f"Prioridad: {tarea.prioridad}  ·  {tarea.fecha}",
                font=("Segoe UI", 8), bg="#181825", fg=self.COLORES_PRIORIDAD.get(tarea.prioridad, "#a6adc8")
            ).grid(row=1, column=1, sticky="w")

            btn_borrar = tk.Button(
                fila, text="X", command=lambda i=idx: self._eliminar_tarea(i),
                bg="#181825", fg="#f38ba8", relief="flat", font=("Segoe UI", 11, "bold"),
                cursor="hand2", bd=0
            )
            btn_borrar.grid(row=0, column=2, rowspan=2, padx=8)

        pendientes = sum(1 for t in self.tareas if not t.completada)
        self.label_estado.config(text=f"{pendientes} tarea(s) pendiente(s) de {len(self.tareas)} en total")

    # ---------- Lógica de negocio ----------
    def _agregar_tarea(self):
        texto = self.entrada_texto.get().strip()
        if not texto:
            messagebox.showwarning("Aviso", "Escribe una tarea antes de agregarla.")
            return
        prioridad = self.combo_prioridad.get()
        self.tareas.append(Tarea(texto, prioridad))
        self.guardar_tareas()
        self.entrada_texto.delete(0, tk.END)
        self._refrescar_lista()

    def _marcar_completada(self, idx, valor):
        self.tareas[idx].completada = valor
        self.guardar_tareas()
        self._refrescar_lista()

    def _eliminar_tarea(self, idx):
        del self.tareas[idx]
        self.guardar_tareas()
        self._refrescar_lista()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = GestorTareasApp(ventana)
    ventana.mainloop()
