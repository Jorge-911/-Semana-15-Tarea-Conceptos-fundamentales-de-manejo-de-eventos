#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación GUI de Lista de Tareas con Tkinter

Características:
- Entrada de texto para nuevas tareas
- Botones: Añadir Tarea, Marcar como Completada, Eliminar Tarea
- Lista de tareas (Listbox) con estados
- Atajos:
    * Enter en el Entry -> añadir tarea
    * Doble clic en una tarea -> alternar completada
    * Barra espaciadora con una tarea seleccionada -> alternar completada
    * Supr/Backspace -> eliminar tarea seleccionada
    * Ctrl+N -> enfocar entrada de texto
- Cambios visuales al completar: prefijo ✓ y color gris
- Código organizado en clase con comentarios
"""
import tkinter as tk
from tkinter import ttk, messagebox


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lista de Tareas")
        self.geometry("520x420")
        self.minsize(420, 360)
        self._create_styles()
        self._create_widgets()
        self._create_bindings()
        # Estructura interna de datos: lista de dicts {"text": str, "done": bool}
        self.tasks = []

    # ---------- UI ----------
    def _create_styles(self):
        # Estilo base para botones y labels
        style = ttk.Style(self)
        # Usa tema disponible
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))

    def _create_widgets(self):
        # Marco superior (título)
        top = ttk.Frame(self, padding=(10, 10, 10, 0))
        top.pack(fill="x")
        ttk.Label(top, text="Mi Lista de Tareas", style="Title.TLabel").pack(anchor="w")

        # Marco de entrada y botón Añadir
        entry_frame = ttk.Frame(self, padding=10)
        entry_frame.pack(fill="x")
        self.task_var = tk.StringVar()
        self.entry = ttk.Entry(entry_frame, textvariable=self.task_var)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.add_btn = ttk.Button(entry_frame, text="Añadir Tarea", command=self.add_task)
        self.add_btn.pack(side="left")

        # Marco de lista y scrollbar
        list_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        list_frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.BROWSE,
            activestyle="none",
            height=12
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Tips/ayuda
        help_lbl = ttk.Label(
            self,
            padding=(10, 0, 10, 6),
            text="Consejos: Enter añade • Doble clic o Espacio marca • Supr elimina • Ctrl+N enfoca entrada",
            foreground="#555"
        )
        help_lbl.pack(fill="x")

        # Marco de botones de acción
        action = ttk.Frame(self, padding=10)
        action.pack(fill="x")
        self.toggle_btn = ttk.Button(action, text="Marcar como Completada", command=self.toggle_selected)
        self.toggle_btn.pack(side="left")
        ttk.Label(action, text=" ").pack(side="left")  # separador visual
        self.delete_btn = ttk.Button(action, text="Eliminar Tarea", command=self.delete_selected)
        self.delete_btn.pack(side="left")

    def _create_bindings(self):
        # Enter en el Entry -> añadir
        self.entry.bind("<Return>", lambda e: self.add_task())
        # Ctrl+N -> enfocar entrada
        self.bind_all("<Control-n>", lambda e: (self.entry.focus_set(), "break"))
        # Doble clic en item -> alternar completada
        self.listbox.bind("<Double-Button-1>", lambda e: self.toggle_selected())
        # Espacio con selección -> alternar
        self.listbox.bind("<space>", self._on_space_toggle)
        # Supr/Backspace -> eliminar
        self.listbox.bind("<Delete>", lambda e: self.delete_selected())
        self.listbox.bind("<BackSpace>", lambda e: self.delete_selected())
        # Mantener botones habilitados/deshabilitados
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._refresh_buttons())

        # Enfocar entrada por defecto
        self.after(100, lambda: self.entry.focus_set())

    # ---------- Lógica de tareas ----------
    def add_task(self):
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
        display = self._format_task(task)
        self.listbox.insert(tk.END, display)
        # Estilo visual según estado
        idx = self.listbox.size() - 1
        self._style_item(idx, task["done"])

    def _format_task(self, task):
        prefix = "✓ " if task["done"] else "• "
        return f"{prefix}{task['text']}"

    def _style_item(self, index, done):
        # Cambiar color según estado (gris si completada)
        try:
            if done:
                self.listbox.itemconfig(index, fg="#888")
            else:
                self.listbox.itemconfig(index, fg="#000")
        except tk.TclError:
            # Algunos temas pueden no soportar itemconfig; ignorar
            pass

    def _selected_index(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def toggle_selected(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Sin selección", "Selecciona una tarea para marcar/desmarcar.")
            return
        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        # Actualizar visualmente
        self.listbox.delete(idx)
        self.listbox.insert(idx, self._format_task(self.tasks[idx]))
        self._style_item(idx, self.tasks[idx]["done"])
        self.listbox.selection_set(idx)
        self._refresh_buttons()

    def delete_selected(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Sin selección", "Selecciona una tarea para eliminar.")
            return
        del self.tasks[idx]
        self.listbox.delete(idx)
        # Ajustar selección
        if self.tasks:
            new_idx = min(idx, len(self.tasks) - 1)
            self.listbox.selection_set(new_idx)
        self._refresh_buttons()

    # ---------- Eventos auxiliares ----------
    def _on_space_toggle(self, event):
        # Solo si hay selección
        if self._selected_index() is not None:
            self.toggle_selected()
            return "break"  # evita que el espacio haga scroll

    def _refresh_buttons(self):
        has_sel = self._selected_index() is not None
        state = "normal" if has_sel else "disabled"
        self.toggle_btn.state([state])
        self.delete_btn.state([state])


def main():
    app = TodoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
