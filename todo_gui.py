#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación GUI de Lista de Tareas con Tkinter

Decisiones de diseño:
- Usamos Tkinter porque es parte de la librería estándar de Python, lo que evita dependencias externas.
- Se optó por una clase `TodoApp` que hereda de `tk.Tk` para mantener la aplicación organizada y modular.
- La lista de tareas se representa internamente como una lista de diccionarios con clave `text` y `done`.
- Se usa un Listbox porque es simple, soporta selección y permite aplicar estilos básicos a cada tarea.
- Los eventos de teclado y ratón (Enter, doble clic, Supr, etc.) se conectan con acciones lógicas,
  mejorando la usabilidad y velocidad para el usuario.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lista de Tareas")
        self.geometry("520x420")
        self.minsize(420, 360)

        # Crear estilos, widgets y bindings (atajos/eventos)
        self._create_styles()
        self._create_widgets()
        self._create_bindings()

        # Estructura interna: lista de dicts {"text": str, "done": bool}
        self.tasks = []

    # ---------- Estilos de la interfaz ----------
    def _create_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():  # Tema visual estable
            style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))

    # ---------- Widgets principales ----------
    def _create_widgets(self):
        # Título superior
        top = ttk.Frame(self, padding=(10, 10, 10, 0))
        top.pack(fill="x")
        ttk.Label(top, text="Mi Lista de Tareas", style="Title.TLabel").pack(anchor="w")

        # Entrada + botón añadir
        entry_frame = ttk.Frame(self, padding=10)
        entry_frame.pack(fill="x")
        self.task_var = tk.StringVar()
        self.entry = ttk.Entry(entry_frame, textvariable=self.task_var)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.add_btn = ttk.Button(entry_frame, text="Añadir Tarea", command=self.add_task)
        self.add_btn.pack(side="left")

        # Lista con scrollbar
        list_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        list_frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(list_frame, selectmode=tk.BROWSE, activestyle="none", height=12)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Ayuda al usuario (atajos disponibles)
        help_lbl = ttk.Label(
            self,
            padding=(10, 0, 10, 6),
            text="Consejos: Enter añade • Doble clic o Espacio marca • Supr elimina • Ctrl+N enfoca entrada",
            foreground="#555"
        )
        help_lbl.pack(fill="x")

        # Botones inferiores (acciones sobre tarea seleccionada)
        action = ttk.Frame(self, padding=10)
        action.pack(fill="x")
        self.toggle_btn = ttk.Button(action, text="Marcar como Completada", command=self.toggle_selected)
        self.toggle_btn.pack(side="left")
        ttk.Label(action, text=" ").pack(side="left")  # Espacio visual
        self.delete_btn = ttk.Button(action, text="Eliminar Tarea", command=self.delete_selected)
        self.delete_btn.pack(side="left")

    # ---------- Manejo de eventos y atajos ----------
    def _create_bindings(self):
        # Enter en el Entry → añadir tarea
        self.entry.bind("<Return>", lambda e: self.add_task())
        # Ctrl+N → enfocar entrada de texto
        self.bind_all("<Control-n>", lambda e: (self.entry.focus_set(), "break"))
        # Doble clic en tarea → alternar completada
        self.listbox.bind("<Double-Button-1>", lambda e: self.toggle_selected())
        # Espacio con tarea seleccionada → alternar completada
        self.listbox.bind("<space>", self._on_space_toggle)
        # Supr/Backspace → eliminar tarea seleccionada
        self.listbox.bind("<Delete>", lambda e: self.delete_selected())
        self.listbox.bind("<BackSpace>", lambda e: self.delete_selected())
        # Actualizar estado de botones según selección
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._refresh_buttons())

        # Al iniciar, enfocar directamente el campo de entrada
        self.after(100, lambda: self.entry.focus_set())

    # ---------- Lógica principal ----------
    def add_task(self):
        """Añadir nueva tarea desde el Entry a la lista interna y al Listbox."""
        text = self.task_var.get().strip()
        if not text:
            messagebox.showinfo("Vacío", "Escribe una tarea antes de añadir.")
            return
        task = {"text": text, "done": False}
        self.tasks.append(task)
        self._insert_listbox_item(task)
        self.task_var.set("")
        self.entry.focus_set()

    def _insert_listbox_item(self, task):
        """Insertar visualmente la tarea en el Listbox."""
        display = self._format_task(task)
        self.listbox.insert(tk.END, display)
        idx = self.listbox.size() - 1
        self._style_item(idx, task["done"])

    def _format_task(self, task):
        """Prefijo distinto según si está completada o no."""
        prefix = "✓ " if task["done"] else "• "
        return f"{prefix}{task['text']}"

    def _style_item(self, index, done):
        """Cambiar color del texto: gris si completada, negro si pendiente."""
        try:
            self.listbox.itemconfig(index, fg="#888" if done else "#000")
        except tk.TclError:
            pass  # algunos temas no soportan colores en Listbox

    def _selected_index(self):
        """Obtener el índice de la tarea seleccionada, o None si no hay."""
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def toggle_selected(self):
        """Alternar estado completado de la tarea seleccionada."""
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Sin selección", "Selecciona una tarea para marcar/desmarcar.")
            return
        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        # Actualizar visualmente el Listbox
        self.listbox.delete(idx)
        self.listbox.insert(idx, self._format_task(self.tasks[idx]))
        self._style_item(idx, self.tasks[idx]["done"])
        self.listbox.selection_set(idx)
        self._refresh_buttons()

    def delete_selected(self):
        """Eliminar la tarea seleccionada de la lista interna y del Listbox."""
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Sin selección", "Selecciona una tarea para eliminar.")
            return
        del self.tasks[idx]
        self.listbox.delete(idx)
        # Ajustar selección tras borrado
        if self.tasks:
            new_idx = min(idx, len(self.tasks) - 1)
            self.listbox.selection_set(new_idx)
        self._refresh_buttons()

    # ---------- Eventos auxiliares ----------
    def _on_space_toggle(self, event):
        """Usar espacio para alternar completada sin que la lista haga scroll."""
        if self._selected_index() is not None:
            self.toggle_selected()
            return "break"  # Evita el comportamiento por defecto

    def _refresh_buttons(self):
        """Habilitar o deshabilitar botones según si hay selección."""
        has_sel = self._selected_index() is not None
        state = "normal" if has_sel else "disabled"
        self.toggle_btn.state([state])
        self.delete_btn.state([state])


def main():
    app = TodoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
