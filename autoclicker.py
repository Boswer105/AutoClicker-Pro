import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController, KeyCode
from pynput import keyboard

# ============================================================
#  AUTCLICKER PRO — VERSION FINALE CORRIGÉE V2
# ============================================================

class AutoClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖱️ AutoClicker Pro")
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # État
        self.clicking = False
        self.thread = None
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.actions = []
        self.hotkey_start = keyboard.Key.f6
        self.hotkey_stop  = keyboard.Key.f7
        self.hotkey_add   = keyboard.Key.f1
        
        # Pour la capture de touche
        self.capturing_key = False
        self.captured_key_callback = None
        self.key_capture_listener = None

        self.build_ui()
        self.start_hotkey_listener()

    # --------------------------------------------------------
    #  INTERFACE
    # --------------------------------------------------------
    def build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"),
                        foreground="#89b4fa")

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        # --- Titre ---
        ttk.Label(main, text="🖱️ AutoClicker Pro", style="Header.TLabel").pack(pady=(0,10))

        # --- Paramètres de clic ---
        frame_settings = ttk.LabelFrame(main, text=" Paramètres de clic ", padding=10)
        frame_settings.pack(fill="x", pady=5)

        row1 = ttk.Frame(frame_settings); row1.pack(fill="x", pady=3)
        ttk.Label(row1, text="Vitesse (CPS):").pack(side="left")
        self.cps_var = tk.StringVar(value="10")
        ttk.Entry(row1, textvariable=self.cps_var, width=8).pack(side="left", padx=5)

        ttk.Label(row1, text="Bouton:").pack(side="left", padx=(20,5))
        self.btn_var = tk.StringVar(value="Gauche")
        ttk.Combobox(row1, textvariable=self.btn_var,
                     values=["Aucun","Gauche","Droit","Milieu"], width=10,
                     state="readonly").pack(side="left")

        row2 = ttk.Frame(frame_settings); row2.pack(fill="x", pady=3)
        ttk.Label(row2, text="Type:").pack(side="left")
        self.type_var = tk.StringVar(value="Simple")
        ttk.Combobox(row2, textvariable=self.type_var,
                     values=["Simple","Double"], width=10,
                     state="readonly").pack(side="left", padx=5)

        ttk.Label(row2, text="Mode:").pack(side="left", padx=(20,5))
        self.mode_var = tk.StringVar(value="Position actuelle")
        ttk.Combobox(row2, textvariable=self.mode_var,
                     values=["Position actuelle","Multi-actions"], width=15,
                     state="readonly").pack(side="left")

        # --- Hotkeys avec indicateur ---
        frame_hot = ttk.LabelFrame(main, text=" Raccourcis clavier ", padding=10)
        frame_hot.pack(fill="x", pady=5)
        
        hot_row = ttk.Frame(frame_hot); hot_row.pack(fill="x")
        
        # Indicateur LED
        self.led_canvas = tk.Canvas(hot_row, width=20, height=20, 
                                     bg="#1e1e2e", highlightthickness=0)
        self.led_canvas.pack(side="left", padx=(0,5))
        self.led_circle = self.led_canvas.create_oval(2, 2, 18, 18, 
                                                       fill="#f38ba8", outline="#f38ba8")
        
        ttk.Label(hot_row, text="▶  Démarrer / Arrêter :  F6",
                  foreground="#a6e3a1").pack(side="left")
        ttk.Label(frame_hot, text="➕ Ajouter un point :  F1",
                  foreground="#89dceb").pack(anchor="w")
        ttk.Label(frame_hot, text="⏹  Quitter l'application :  F7",
                  foreground="#f38ba8").pack(anchor="w")

        # --- Multi-actions ---
        frame_actions = ttk.LabelFrame(main, text=" Actions (mode Multi-actions) ", padding=10)
        frame_actions.pack(fill="both", expand=True, pady=5)

        btns = ttk.Frame(frame_actions); btns.pack(fill="x", pady=(0,5))
        ttk.Button(btns, text="🖱️ Clic",
                   command=self.add_click_action).pack(side="left", padx=2)
        ttk.Button(btns, text="⌨️ Touche",
                   command=self.add_key_action).pack(side="left", padx=2)
        ttk.Button(btns, text="🔄 Molette",
                   command=self.add_scroll_action).pack(side="left", padx=2)
        ttk.Button(btns, text="🗑️ Supprimer",
                   command=self.del_action).pack(side="left", padx=2)
        ttk.Button(btns, text="✏️ Délai",
                   command=self.edit_delay).pack(side="left", padx=2)
        ttk.Button(btns, text="💾 Sauver",
                   command=self.save_actions).pack(side="right", padx=2)
        ttk.Button(btns, text="📂 Charger",
                   command=self.load_actions).pack(side="right", padx=2)

        cols = ("index", "type", "action", "delay")
        self.tree = ttk.Treeview(frame_actions, columns=cols, show="headings", height=10)
        self.tree.heading("index", text="#")
        self.tree.heading("type", text="Type")
        self.tree.heading("action", text="Action")
        self.tree.heading("delay", text="Délai (s)")
        self.tree.column("index", width=40)
        self.tree.column("type", width=80)
        self.tree.column("action", width=250)
        self.tree.column("delay", width=100)
        self.tree.pack(fill="both", expand=True)

        # --- Boutons principaux ---
        frame_ctrl = ttk.Frame(main); frame_ctrl.pack(fill="x", pady=10)
        self.btn_start = ttk.Button(frame_ctrl, text="▶ DÉMARRER  (F6)",
                                    command=self.toggle_clicking)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(frame_ctrl, text="❌ QUITTER  (F7)",
                   command=self.quit_app).pack(side="left", expand=True, fill="x", padx=5)

        # --- Statut ---
        self.status_var = tk.StringVar(value="⏸️ En attente...")
        self.status_lbl = tk.Label(main, textvariable=self.status_var,
                                   bg="#1e1e2e", fg="#f9e2af",
                                   font=("Segoe UI", 11, "bold"))
        self.status_lbl.pack()

    # --------------------------------------------------------
    #  GESTION DES ACTIONS
    # --------------------------------------------------------
    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, a in enumerate(self.actions, 1):
            if a["type"] == "click":
                desc = f"Clic {a['data']['button']} à ({a['data']['x']}, {a['data']['y']})"
            elif a["type"] == "key":
                desc = f"Touche: {a['data']['key']}"
            elif a["type"] == "scroll":
                desc = f"Molette: {a['data']['direction']} ({a['data']['amount']}x)"
            else:
                desc = "Inconnu"
            self.tree.insert("", "end", values=(idx, a["type"].upper(), desc, a["delay"]))

    def add_click_action(self):
        x, y = self.mouse.position
        self.actions.append({
            "type": "click",
            "data": {"x": x, "y": y, "button": self.btn_var.get()},
            "delay": 0.5
        })
        self.refresh_tree()
        self.status_var.set(f"✅ Clic ajouté en ({x}, {y})")

    def add_key_action(self):
        win = tk.Toplevel(self.root)
        win.title("Appuie sur une touche")
        win.geometry("350x150")
        win.configure(bg="#1e1e2e")
        
        ttk.Label(win, text="Appuie sur la touche à enregistrer :",
                  foreground="#cdd6f4", background="#1e1e2e",
                  font=("Segoe UI", 11)).pack(pady=15)
        
        key_label = ttk.Label(win, text="En attente...",
                              foreground="#f9e2af", background="#1e1e2e",
                              font=("Segoe UI", 14, "bold"))
        key_label.pack(pady=10)
        
        # Créer un nouveau listener dédié pour la capture
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char is not None:
                    key_str = key.char
                elif hasattr(key, 'name'):
                    key_str = key.name
                else:
                    key_str = str(key)
                
                # Désactiver ce listener après capture
                self.key_capture_listener.stop()
                self.key_capture_listener = None
                
                # Mettre à jour l'affichage et sauvegarder
                win.after(0, lambda: key_label.config(text=f"Touche: {key_str}"))
                win.after(500, lambda: self._save_key_action(key_str, win))
                
                return False  # Arrêter le listener
            except Exception as e:
                print(f"Erreur capture: {e}")
                return True
        
        # Stopper tout listener précédent s'il existe
        if self.key_capture_listener:
            try:
                self.key_capture_listener.stop()
            except:
                pass
        
        # Démarrer le nouveau listener de capture
        self.key_capture_listener = keyboard.Listener(on_press=on_press)
        self.key_capture_listener.daemon = True
        self.key_capture_listener.start()

    def _save_key_action(self, key_str, win):
        self.actions.append({
            "type": "key",
            "data": {"key": key_str},
            "delay": 0.5
        })
        self.refresh_tree()
        self.status_var.set(f"✅ Touche '{key_str}' ajoutée")
        try:
            win.destroy()
        except:
            pass

    def add_scroll_action(self):
        win = tk.Toplevel(self.root)
        win.title("Molette")
        win.geometry("300x150")
        win.configure(bg="#1e1e2e")
        ttk.Label(win, text="Direction:", foreground="#cdd6f4", background="#1e1e2e").pack(pady=5)
        dir_var = tk.StringVar(value="Haut")
        ttk.Combobox(win, textvariable=dir_var, values=["Haut","Bas"],
                     state="readonly", width=10).pack()
        ttk.Label(win, text="Nombre de crans:", foreground="#cdd6f4", background="#1e1e2e").pack(pady=5)
        amt_var = tk.StringVar(value="3")
        ttk.Entry(win, textvariable=amt_var, width=10).pack()
        def ok():
            try:
                amount = int(amt_var.get())
                self.actions.append({
                    "type": "scroll",
                    "data": {"direction": dir_var.get(), "amount": amount},
                    "delay": 0.5
                })
                self.refresh_tree()
                self.status_var.set(f"✅ Molette {dir_var.get()} x{amount} ajoutée")
                win.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Nombre invalide")
        ttk.Button(win, text="OK", command=ok).pack(pady=5)

    def del_action(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionne une ligne à supprimer.")
            return
        idx = self.tree.index(sel[0])
        self.actions.pop(idx)
        self.refresh_tree()

    def edit_delay(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionne une ligne.")
            return
        idx = self.tree.index(sel[0])
        win = tk.Toplevel(self.root)
        win.title("Délai")
        win.geometry("250x100")
        win.configure(bg="#1e1e2e")
        ttk.Label(win, text="Nouveau délai (secondes):",
                  foreground="#cdd6f4", background="#1e1e2e").pack(pady=10)
        var = tk.StringVar(value=str(self.actions[idx]["delay"]))
        e = ttk.Entry(win, textvariable=var, width=10)
        e.pack()
        def ok():
            try:
                self.actions[idx]["delay"] = float(var.get())
                self.refresh_tree()
                win.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Valeur invalide")
        ttk.Button(win, text="OK", command=ok).pack(pady=5)

    def save_actions(self):
        with open("autoclicker_actions.json", "w", encoding="utf-8") as f:
            json.dump(self.actions, f, ensure_ascii=False, indent=2)
        self.status_var.set("💾 Actions sauvegardées")

    def load_actions(self):
        if not os.path.exists("autoclicker_actions.json"):
            messagebox.showinfo("Info", "Aucune sauvegarde trouvée.")
            return
        with open("autoclicker_actions.json", encoding="utf-8") as f:
            self.actions = json.load(f)
        self.refresh_tree()
        self.status_var.set("📂 Actions chargées")

    # --------------------------------------------------------
    #  LOGIQUE D'EXÉCUTION
    # --------------------------------------------------------
    def toggle_clicking(self):
        if self.clicking:
            self.clicking = False
            self.status_var.set("⏸️ En attente...")
            self.btn_start.config(text="▶ DÉMARRER  (F6)")
            self.led_canvas.itemconfig(self.led_circle, fill="#f38ba8", outline="#f38ba8")
        else:
            try:
                cps = float(self.cps_var.get())
                if cps <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erreur", "Vitesse invalide (CPS > 0)")
                return
            self.clicking = True
            self.status_var.set(f"🔥 EN COURS — {cps} CPS")
            self.btn_start.config(text="⏸ ARRÊTER  (F6)")
            self.led_canvas.itemconfig(self.led_circle, fill="#a6e3a1", outline="#a6e3a1")
            self.thread = threading.Thread(target=self.action_loop, daemon=True)
            self.thread.start()

    def action_loop(self):
        cps = float(self.cps_var.get())
        interval = 1.0 / cps
        mode = self.mode_var.get()
        double = self.type_var.get() == "Double"

        if mode == "Position actuelle":
            btn_name = self.btn_var.get()
            if btn_name == "Aucun":
                self.status_var.set("⚠️ Mode Position actuelle nécessite un bouton")
                self.clicking = False
                self.led_canvas.itemconfig(self.led_circle, fill="#f38ba8", outline="#f38ba8")
                return
            btn = {"Gauche": Button.left, "Droit": Button.right,
                   "Milieu": Button.middle}[btn_name]
            while self.clicking:
                self.mouse.click(btn, 2 if double else 1)
                time.sleep(interval)
        else:  # Multi-actions
            if not self.actions:
                self.status_var.set("⚠️ Aucune action définie !")
                self.clicking = False
                self.led_canvas.itemconfig(self.led_circle, fill="#f38ba8", outline="#f38ba8")
                return
            while self.clicking:
                for action in self.actions:
                    if not self.clicking:
                        break
                    self.execute_action(action, double)
                    time.sleep(action["delay"])

    def execute_action(self, action, double=False):
        if action["type"] == "click":
            data = action["data"]
            if data["button"] == "Aucun":
                return  # Pas de clic
            self.mouse.position = (data["x"], data["y"])
            time.sleep(0.05)
            btn = {"Gauche": Button.left, "Droit": Button.right,
                   "Milieu": Button.middle}[data["button"]]
            self.mouse.click(btn, 2 if double else 1)
        elif action["type"] == "key":
            key_str = action["data"]["key"]
            try:
                # Mapping des touches spéciales
                special_keys_map = {
                    "space": Key.space,
                    "enter": Key.enter,
                    "tab": Key.tab,
                    "escape": Key.esc,
                    "esc": Key.esc,
                    "backspace": Key.backspace,
                    "delete": Key.delete,
                    "up": Key.up,
                    "down": Key.down,
                    "left": Key.left,
                    "right": Key.right,
                    "ctrl_l": Key.ctrl_l,
                    "ctrl_r": Key.ctrl_r,
                    "alt_l": Key.alt_l,
                    "alt_r": Key.alt_r,
                    "shift_l": Key.shift_l,
                    "shift_r": Key.shift_r,
                    "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
                    "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
                    "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
                    "home": Key.home, "end": Key.end,
                    "page_up": Key.page_up, "page_down": Key.page_down,
                    "insert": Key.insert,
                    "caps_lock": Key.caps_lock,
                    "num_lock": Key.num_lock,
                    "scroll_lock": Key.scroll_lock,
                }
                
                # Vérifier si c'est une touche spéciale connue
                if key_str.lower() in special_keys_map:
                    k = special_keys_map[key_str.lower()]
                    self.keyboard.press(k)
                    self.keyboard.release(k)
                else:
                    # Pour les caractères normaux, press/release directement
                    self.keyboard.press(key_str)
                    self.keyboard.release(key_str)
                    
            except Exception as e:
                print(f"Erreur touche '{key_str}': {e}")
        elif action["type"] == "scroll":
            data = action["data"]
            direction = data["direction"]
            amount = data["amount"]
            
            try:
                # scroll(dx, dy) - dy positif = vers le haut, négatif = vers le bas
                if direction == "Haut":
                    self.mouse.scroll(0, amount)
                else:  # Bas
                    self.mouse.scroll(0, -amount)
            except AttributeError:
                # Si scroll n'existe pas, essayer avec une autre méthode
                print("La méthode scroll n'est pas disponible dans cette version de pynput")
                messagebox.showwarning("Attention", 
                    "Le scroll de molette n'est pas supporté par votre version de pynput.\n"
                    "Mettez à jour pynput : pip install --upgrade pynput")

    # --------------------------------------------------------
    #  HOTKEYS GLOBALES
    # --------------------------------------------------------
    def start_hotkey_listener(self):
        def on_press(key):
            # Ne pas traiter les hotkeys si un listener de capture est actif
            if self.key_capture_listener:
                return
            
            if key == self.hotkey_start:
                self.root.after(0, self.toggle_clicking)
            elif key == self.hotkey_stop:
                self.root.after(0, self.quit_app)
            elif key == self.hotkey_add:
                self.root.after(0, self.add_click_action)

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

    def quit_app(self):
        self.clicking = False
        try:
            self.listener.stop()
        except Exception:
            pass
        try:
            if self.key_capture_listener:
                self.key_capture_listener.stop()
        except Exception:
            pass
        self.root.quit()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()


if __name__ == "__main__":
    AutoClicker().run()