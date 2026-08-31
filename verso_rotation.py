import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageWin
import fitz
import win32print
import win32ui

ctk.set_appearance_mode("dark")

ACCENT   = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
SUCCESS  = "#16A34A"
BG_DARK  = "#0F172A"
BG_CARD  = "#1E293B"
BG_INPUT = "#334155"
TEXT_PRI = "#F8FAFC"
TEXT_SEC = "#94A3B8"
DANGER   = "#EF4444"
WARN     = "#F59E0B"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bon de commande - Recto / Verso")
        self.geometry("1200x750")
        self.minsize(1000, 680)
        self.configure(fg_color=BG_DARK)

        # Variables PDF et Imprimante
        self.pdf_path     = None
        self.pdf_doc      = None
        self.recto_idx    = 0
        self.n_pages      = 0
        self.printer_name = win32print.GetDefaultPrinter()

        self._raw_source_img = None
        self._raw_print_img = None
        self._resize_job = None
        self.thumbnail_buttons = []
        
        self.pos_x_var = ctk.DoubleVar(value=0.05)
        self.pos_y_var = ctk.DoubleVar(value=0.98)
        self._slider_job = None

        # --- GESTION DES LANGUES ---
        self.current_lang = "FR"
        self.loc = {
            "FR": {
                "header": "📄 Préparation bon de commande",
                "no_pdf_top": "Aucun PDF chargé. Glissez un fichier ci-dessous.",
                "drop_zone": "📂 Glissez un PDF ici\nou cliquez pour choisir",
                "add_text": "✏️ Texte à ajouter sur le recto",
                "size": "Taille :",
                "printer": "🖨️ Imprimante",
                "print_btn": "🖨️ Imprimer",
                "sel_page": "📄 Page sélectionnée",
                "preview": "🖨️ Aperçu impression",
                "no_pdf_prev": "- aucun PDF -",
                "loading": "⏳ Chargement des pages...",
                "printing": "Impression en cours…",
                "success": "✅ Envoyé à l'imprimante !",
                "page_lbl": "Page",
                "no_printer": "Aucune imprimante",
                "dialog_title": "Choisir un PDF"
            },
            "EN": {
                "header": "📄 Order Form Preparation",
                "no_pdf_top": "No PDF loaded. Drag and drop a file below.",
                "drop_zone": "📂 Drag a PDF here\nor click to browse",
                "add_text": "✏️ Text to add on the front",
                "size": "Size:",
                "printer": "🖨️ Printer",
                "print_btn": "🖨️ Print",
                "sel_page": "📄 Selected Page",
                "preview": "🖨️ Print Preview",
                "no_pdf_prev": "- no PDF -",
                "loading": "⏳ Loading pages...",
                "printing": "Printing...",
                "success": "✅ Sent to printer!",
                "page_lbl": "Page",
                "no_printer": "No printer found",
                "dialog_title": "Choose a PDF"
            }
        }

        self._build_ui()
        self._enable_drag_drop()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=56, border_width=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        self.header_lbl = ctk.CTkLabel(header, text=self.loc[self.current_lang]["header"], font=ctk.CTkFont(size=17, weight="bold"), text_color=TEXT_PRI)
        self.header_lbl.pack(side="left", padx=24, pady=14)

        # Bouton Langue
        self.lang_btn = ctk.CTkButton(header, text="🌐 EN", width=100, fg_color="transparent", hover_color=BG_INPUT, font=ctk.CTkFont(size=22, weight="bold"), command=self._toggle_lang)
        self.lang_btn.pack(side="right", padx=24, pady=14)

        # Corps
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=16)
        body.grid_columnconfigure(0, weight=1, minsize=350)
        body.grid_columnconfigure(1, weight=3)
        body.grid_rowconfigure(0, weight=0)
        body.grid_rowconfigure(1, weight=1)

        # Barre des miniatures
        self.thumb_frame = ctk.CTkScrollableFrame(body, orientation="horizontal", height=125, fg_color=BG_CARD, corner_radius=14)
        self.thumb_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        
        self.loading_lbl = ctk.CTkLabel(self.thumb_frame, text=self.loc[self.current_lang]["no_pdf_top"], text_color=TEXT_SEC)
        self.loading_lbl.pack(padx=20, pady=40)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)

        self.drop_frame = ctk.CTkFrame(left, fg_color=BG_INPUT, corner_radius=12, border_width=1, border_color=ACCENT)
        self.drop_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 6))
        
        self.drop_label = ctk.CTkLabel(self.drop_frame, text=self.loc[self.current_lang]["drop_zone"], font=ctk.CTkFont(size=13), text_color=TEXT_SEC, justify="center")
        self.drop_label.pack(padx=16, pady=20)
        self.drop_frame.bind("<Button-1>", lambda e: self._open_file())
        self.drop_label.bind("<Button-1>", lambda e: self._open_file())

        self.file_label = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=11), text_color=ACCENT)
        self.file_label.grid(row=1, column=0, padx=16, pady=(0, 4))

        ctk.CTkFrame(left, fg_color=BG_INPUT, height=1).grid(row=2, column=0, sticky="ew", padx=16, pady=6)

        self.add_text_lbl = ctk.CTkLabel(left, text=self.loc[self.current_lang]["add_text"], font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRI)
        self.add_text_lbl.grid(row=3, column=0, sticky="w", padx=16, pady=(6,2))
        
        tools_frame = ctk.CTkFrame(left, fg_color="transparent")
        tools_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 4))
        
        self.size_lbl = ctk.CTkLabel(tools_frame, text=self.loc[self.current_lang]["size"], font=ctk.CTkFont(size=11), text_color=TEXT_SEC)
        self.size_lbl.pack(side="left", padx=(0, 6))
        
        self.font_size_var = ctk.StringVar(value="14")
        self.font_size_menu = ctk.CTkOptionMenu(tools_frame, variable=self.font_size_var, values=["10", "12", "14", "16", "20", "24", "32"],
                                                command=lambda e: self._refresh_print_preview(), width=60, height=24, font=ctk.CTkFont(size=11),
                                                fg_color=BG_INPUT, button_color=ACCENT, button_hover_color=ACCENT_HOVER)
        self.font_size_menu.pack(side="left")

        self.text_input = ctk.CTkTextbox(left, height=80, font=ctk.CTkFont(size=12), fg_color=BG_INPUT, border_color=ACCENT, border_width=1, text_color=TEXT_PRI)
        self.text_input.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 6))
        self.text_input.bind("<KeyRelease>", lambda e: self._refresh_print_preview())

        pos_frame = ctk.CTkFrame(left, fg_color="transparent")
        pos_frame.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 6))
        ctk.CTkLabel(pos_frame, text="↔️ X :", font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(side="left")
        self.slider_x = ctk.CTkSlider(pos_frame, variable=self.pos_x_var, from_=0.0, to=1.0, command=self._on_slider_change,
                                      width=90, fg_color=BG_INPUT, progress_color=SUCCESS, button_color=ACCENT, button_hover_color=ACCENT_HOVER)
        self.slider_x.pack(side="left", padx=(4, 16))
        ctk.CTkLabel(pos_frame, text="↕️ Y :", font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(side="left")
        self.slider_y = ctk.CTkSlider(pos_frame, variable=self.pos_y_var, from_=0.0, to=1.0, command=self._on_slider_change,
                                      width=90, fg_color=BG_INPUT, progress_color=SUCCESS, button_color=ACCENT, button_hover_color=ACCENT_HOVER)
        self.slider_y.pack(side="left", padx=4)

        ctk.CTkFrame(left, fg_color=BG_INPUT, height=1).grid(row=7, column=0, sticky="ew", padx=16, pady=6)

        self.printer_lbl = ctk.CTkLabel(left, text=self.loc[self.current_lang]["printer"], font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRI)
        self.printer_lbl.grid(row=8, column=0, sticky="w", padx=16, pady=(6,2))
        
        printers = self._get_printers()
        default  = self.printer_name if self.printer_name in printers else (printers[0] if printers else "")
        self.printer_var = ctk.StringVar(value=default)
        self.printer_menu = ctk.CTkOptionMenu(left, variable=self.printer_var, values=printers if printers else [self.loc[self.current_lang]["no_printer"]],
                                              command=self._on_printer_change, fg_color=BG_INPUT, button_color=ACCENT, button_hover_color=ACCENT_HOVER, dropdown_fg_color=BG_CARD)
        self.printer_menu.grid(row=9, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.print_btn = ctk.CTkButton(left, text=self.loc[self.current_lang]["print_btn"], font=ctk.CTkFont(size=15, weight="bold"),
                                       fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#FFFFFF", height=46, command=self._do_print, state="disabled")
        self.print_btn.grid(row=10, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.status_label = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=11), text_color=TEXT_SEC)
        self.status_label.grid(row=11, column=0, padx=16, pady=(0, 12))

    def _build_right(self, parent):
        self.right_frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14)
        self.right_frame.grid(row=1, column=1, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1, uniform="col")
        self.right_frame.grid_columnconfigure(1, weight=1, uniform="col")
        self.right_frame.grid_rowconfigure(1, weight=1)

        self.right_frame.bind("<Configure>", self._on_right_frame_resize)

        self.sel_page_lbl = ctk.CTkLabel(self.right_frame, text=self.loc[self.current_lang]["sel_page"], font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT)
        self.sel_page_lbl.grid(row=0, column=0, pady=(14, 4))
        
        self.preview_lbl = ctk.CTkLabel(self.right_frame, text=self.loc[self.current_lang]["preview"], font=ctk.CTkFont(size=12, weight="bold"), text_color=WARN)
        self.preview_lbl.grid(row=0, column=1, pady=(14, 4))

        self.prev_source = ctk.CTkLabel(self.right_frame, text=self.loc[self.current_lang]["no_pdf_prev"], text_color=TEXT_SEC, fg_color=BG_INPUT, corner_radius=8)
        self.prev_source.grid(row=1, column=0, sticky="nsew", padx=(16, 6), pady=(0, 16))

        self.prev_print = ctk.CTkLabel(self.right_frame, text=self.loc[self.current_lang]["no_pdf_prev"], text_color=TEXT_SEC, fg_color=BG_INPUT, corner_radius=8)
        self.prev_print.grid(row=1, column=1, sticky="nsew", padx=(6, 16), pady=(0, 16))

    # --- MÉTHODE DE TRADUCTION ---
    def _toggle_lang(self):
        if self.current_lang == "FR":
            self.current_lang = "EN"
            self.lang_btn.configure(text="🌐 FR")
        else:
            self.current_lang = "FR"
            self.lang_btn.configure(text="🌐 EN")
            
        t = self.loc[self.current_lang]
        
        # Mise à jour de tous les textes fixes
        self.header_lbl.configure(text=t["header"])
        if not self.pdf_doc:
            self.loading_lbl.configure(text=t["no_pdf_top"])
            self.drop_label.configure(text=t["drop_zone"])
            self.prev_source.configure(text=t["no_pdf_prev"])
            self.prev_print.configure(text=t["no_pdf_prev"])
            
        self.add_text_lbl.configure(text=t["add_text"])
        self.size_lbl.configure(text=t["size"])
        self.printer_lbl.configure(text=t["printer"])
        self.print_btn.configure(text=t["print_btn"])
        self.sel_page_lbl.configure(text=t["sel_page"])
        self.preview_lbl.configure(text=t["preview"])
        
        if not self._get_printers():
            self.printer_menu.configure(values=[t["no_printer"]])

        # Mise à jour dynamique du texte des boutons de pages
        for i, btn in enumerate(self.thumbnail_buttons):
            btn.configure(text=f"{t['page_lbl']} {i+1}")

    # --- RESTE DU CODE (Inchangé) ---
    def _on_slider_change(self, value):
        if self._slider_job:
            self.after_cancel(self._slider_job)
        self._slider_job = self.after(150, self._refresh_print_preview)

    def _on_right_frame_resize(self, event):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(200, self._resize_previews)

    def _resize_previews(self):
        if self._raw_source_img:
            w, h = max(100, self.prev_source.winfo_width()), max(100, self.prev_source.winfo_height())
            img_copy = self._raw_source_img.copy()
            img_copy.thumbnail((w - 20, h - 20), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.prev_source.configure(image=ctk_img, text="")

        if self._raw_print_img:
            w, h = max(100, self.prev_print.winfo_width()), max(100, self.prev_print.winfo_height())
            img_copy = self._raw_print_img.copy()
            img_copy.thumbnail((w - 20, h - 20), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.prev_print.configure(image=ctk_img, text="")

    def _enable_drag_drop(self):
        try:
            from tkinterdnd2 import DND_FILES
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
        path = event.data.strip().strip("{}")
        if path.lower().endswith(".pdf"):
            self._load_pdf(path)

    def _open_file(self):
        path = filedialog.askopenfilename(title=self.loc[self.current_lang]["dialog_title"], filetypes=[("Fichiers PDF", "*.pdf")])
        if path:
            self._load_pdf(path)

    def _load_pdf(self, path):
        self.pdf_path = path
        self.pdf_doc  = fitz.open(path)
        self.n_pages  = len(self.pdf_doc)
        
        short = os.path.basename(path)
        self.file_label.configure(text=f"✅ {short} ({self.n_pages} p.)", text_color=SUCCESS)
        self.drop_label.configure(text=f"📄 {short}")
        self.print_btn.configure(state="normal")
        self.status_label.configure(text="")

        self._generate_thumbnails()

    def _generate_thumbnails(self):
        for widget in self.thumb_frame.winfo_children():
            widget.destroy()
        self.thumbnail_buttons.clear()

        self.loading_lbl = ctk.CTkLabel(self.thumb_frame, text=self.loc[self.current_lang]["loading"], font=ctk.CTkFont(size=12), text_color=TEXT_SEC)
        self.loading_lbl.pack(padx=20, pady=40)

        threading.Thread(target=self._process_thumbnails, daemon=True).start()

    def _process_thumbnails(self):
        images = []
        try:
            for i in range(self.n_pages):
                page = self.pdf_doc[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2), colorspace=fitz.csGRAY, alpha=False) 
                img = Image.frombytes("L", [pix.width, pix.height], pix.samples).convert("RGB")
                images.append(img)
            self.after(0, self._render_thumbnail_widgets, images)
        except Exception as e:
            print("Erreur miniatures :", e)

    def _render_thumbnail_widgets(self, images):
        if hasattr(self, 'loading_lbl') and self.loading_lbl.winfo_exists():
            self.loading_lbl.destroy()
            
        t = self.loc[self.current_lang]
        for i, img in enumerate(images):
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(55, 75))
            btn = ctk.CTkButton(self.thumb_frame, image=ctk_img, text=f"{t['page_lbl']} {i+1}", compound="top",
                                width=65, height=95, font=ctk.CTkFont(size=11, weight="bold"),
                                fg_color=BG_INPUT, hover_color=ACCENT_HOVER, text_color=TEXT_PRI,
                                border_width=2, border_color=BG_INPUT,
                                command=lambda idx=i: self._select_page(idx))
            btn.pack(side="left", padx=8, pady=2)
            self.thumbnail_buttons.append(btn)
        
        if self.n_pages > 0:
            self._select_page(0)

    def _select_page(self, idx):
        self.recto_idx = idx
        for i, btn in enumerate(self.thumbnail_buttons):
            if i == idx:
                btn.configure(border_color=SUCCESS, fg_color=BG_CARD, text_color=SUCCESS)
            else:
                btn.configure(border_color=BG_INPUT, fg_color=BG_INPUT, text_color=TEXT_PRI)
                
        self._refresh_source_preview()
        self._refresh_print_preview()

    def _refresh_source_preview(self):
        if not self.pdf_doc: return
        def render():
            page = self.pdf_doc[self.recto_idx]
            pix  = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), colorspace=fitz.csGRAY, alpha=False)
            self._raw_source_img = Image.frombytes("L", [pix.width, pix.height], pix.samples).convert("RGB")
            self.after(0, self._resize_previews)
        threading.Thread(target=render, daemon=True).start()

    def _refresh_print_preview(self):
        if not self.pdf_doc: return
        overlay = self.text_input.get("1.0", "end").strip()
        font_size = int(self.font_size_var.get())
        def render():
            try:
                self._raw_print_img = self._build_print_image(overlay, font_size)
                self.after(0, self._resize_previews)
            except Exception as e:
                print(f"Erreur preview : {e}")
        threading.Thread(target=render, daemon=True).start()

    def _generate_sheet_doc(self, overlay_text, font_size):
        A4_W, A4_H = 841.89, 595.28
        HALF, MARGIN = A4_W / 2, 12
        EXTRA_BOTTOM = 60 
        PADDING = 15      

        doc = fitz.open()
        sheet = doc.new_page(width=A4_W, height=A4_H)

        pix_gray = self.pdf_doc[self.recto_idx].get_pixmap(colorspace=fitz.csGRAY, dpi=300, alpha=False)

        full_l = fitz.Rect(MARGIN, MARGIN, HALF - MARGIN, A4_H - MARGIN)
        pdf_dst_l = fitz.Rect(full_l.x0 + PADDING, full_l.y0 + PADDING, full_l.x1 - PADDING, full_l.y1 - EXTRA_BOTTOM)
        sheet.insert_image(pdf_dst_l, pixmap=pix_gray)
        
        if overlay_text:
            box_width = 300
            box_height = font_size * 4
            pos_x_pct = self.pos_x_var.get()
            pos_y_pct = self.pos_y_var.get()
            
            start_x = full_l.x0 + (full_l.width - box_width) * pos_x_pct
            start_y = full_l.y0 + (full_l.height - box_height) * pos_y_pct
            txt_rect = fitz.Rect(start_x, start_y, start_x + box_width, start_y + box_height)
            
            tw = fitz.TextWriter(sheet.rect, color=(0, 0, 0))
            tw.fill_textbox(txt_rect, overlay_text, font=fitz.Font("helv"), fontsize=font_size)
            tw.write_text(sheet)

        sheet.draw_line(fitz.Point(HALF, 8), fitz.Point(HALF, A4_H - 8), color=(0.6, 0.6, 0.6), width=0.5)

        full_r = fitz.Rect(HALF + MARGIN, MARGIN, A4_W - MARGIN, A4_H - MARGIN)
        pdf_dst_r = fitz.Rect(full_r.x0 + PADDING, full_r.y0 + PADDING, full_r.x1 - PADDING, full_r.y1 - EXTRA_BOTTOM)
        sheet.insert_image(pdf_dst_r, pixmap=pix_gray)

        return doc

    def _build_print_image(self, overlay_text, font_size):
        doc = self._generate_sheet_doc(overlay_text, font_size)
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), colorspace=fitz.csRGB)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img

    def _on_printer_change(self, choice):
        self.printer_name = choice

    def _get_printers(self):
        try:
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printers = [p[2] for p in win32print.EnumPrinters(flags)]
            return printers if printers else []
        except Exception:
            return []

    def _send_to_printer(self, printer_name, pil_image):
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        
        horzres = hDC.GetDeviceCaps(8)
        vertres = hDC.GetDeviceCaps(10)
        
        img_w, img_h = pil_image.size
        img_ratio = img_w / img_h
        page_ratio = horzres / vertres
        
        if img_ratio > page_ratio:
            target_w = horzres
            target_h = int(horzres / img_ratio)
        else:
            target_h = vertres
            target_w = int(vertres * img_ratio)
            
        start_x = (horzres - target_w) // 2
        start_y = (vertres - target_h) // 2

        hDC.StartDoc("Impression directe PDF")
        hDC.StartPage()
        
        dib = ImageWin.Dib(pil_image)
        dib.draw(hDC.GetHandleOutput(), (start_x, start_y, start_x + target_w, start_y + target_h))
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

    def _do_print(self):
        if not self.pdf_doc: return
        
        self.status_label.configure(text=self.loc[self.current_lang]["printing"], text_color=TEXT_SEC)
        self.print_btn.configure(state="disabled")

        def run():
            err_msg = ""
            try:
                overlay = self.text_input.get("1.0", "end").strip()
                font_size = int(self.font_size_var.get())
                printer = self.printer_var.get()
                
                doc = self._generate_sheet_doc(overlay, font_size)
                pix = doc[0].get_pixmap(dpi=300, colorspace=fitz.csRGB)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                doc.close()

                self._send_to_printer(printer, img)

            except Exception as exc:
                err_msg = str(exc)

            if err_msg:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {err_msg}", text_color=DANGER))
            else:
                self.after(0, lambda: self.status_label.configure(text=self.loc[self.current_lang]["success"], text_color=SUCCESS))
            self.after(0, lambda: self.print_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app = App()
    app.mainloop()