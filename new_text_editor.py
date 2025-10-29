from customtkinter import *
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import keyboard as key
import json

# ---------- Root ----------
root = CTk()
root.title("Text Editor")

# ---------- Globals ----------
nav_color = None
hover_color = None
text_color = None
text_area_bg = None
# ---------- File type support ----------
FILE_TYPES = [
    ("All files", "*.*"),

    # General text
    ("Text files", "*.txt"),
    ("Log files", "*.log"),
    ("Markdown files", "*.md;*.markdown"),
    ("Rich Text Format", "*.rtf"),
    ("ReadMe files", "README*"),

    # Programming languages
    ("Python files", "*.py"),
    ("C files", "*.c"),
    ("C++ files", "*.cpp;*.cc;*.cxx;*.h;*.hpp"),
    ("C# files", "*.cs"),
    ("Java files", "*.java"),
    ("Kotlin files", "*.kt;*.kts"),
    ("Swift files", "*.swift"),
    ("Go files", "*.go"),
    ("Rust files", "*.rs"),
    ("PHP files", "*.php"),
    ("Perl files", "*.pl;*.pm"),
    ("Ruby files", "*.rb"),
    ("Lua files", "*.lua"),
    ("TypeScript files", "*.ts;*.tsx"),
    ("JavaScript files", "*.js;*.mjs;*.cjs"),
    ("SQL files", "*.sql"),

    # Web / Markup
    ("HTML files", "*.html;*.htm"),
    ("CSS files", "*.css"),
    ("XML files", "*.xml"),
    ("JSON files", "*.json"),
    ("YAML files", "*.yaml;*.yml"),
    ("TOML files", "*.toml"),
    ("Handlebars/Mustache templates", "*.hbs;*.mustache"),
    ("Liquid templates", "*.liquid"),

    # Config / Script
    ("INI/Config files", "*.ini;*.cfg;*.conf"),
    ("Batch files", "*.bat;*.cmd"),
    ("Shell scripts", "*.sh;*.bash"),
    ("PowerShell scripts", "*.ps1;*.psm1;*.psd1"),
    ("Makefiles", "Makefile;makefile;GNUMakefile"),
    ("Dockerfiles", "Dockerfile;dockerfile"),
    ("Kubernetes/YAML manifests", "*.yaml;*.yml"),
    ("Environment files", "*.env"),
    ("Gradle/Maven files", "*.gradle;*.pom;pom.xml"),

    # Data / Documentation
    ("CSV files", "*.csv"),
    ("TSV files", "*.tsv"),
    ("INI files", "*.ini"),
    ("Properties files", "*.properties"),
    ("LaTeX files", "*.tex;*.cls;*.sty"),
    ("BibTeX files", "*.bib"),
    ("Diff/Patch files", "*.diff;*.patch"),

    # Misc text formats
    ("Docker Compose files", "docker-compose*.yml;docker-compose*.yaml"),
    ("Git ignore/config files", ".gitignore;.gitattributes;.gitconfig"),
    ("License files", "LICENSE*;COPYING*"),
    ("JSON Schema files", "*.schema.json"),
]
FONT_STYLES = [
    "Comic Sans MS",
    "Impact",
    "Franklin Gothic Medium",
    "Trebuchet MS",
    "Courier New",
    "Consolas",
    "Lucida Console",
    "Arial",
    "Helvetica",
    "Verdana",
    "Tahoma",
    "Calibri",
    "Segoe UI"
]
def set_font_style(style):
    global settings
    tw = get_active_text_widget()
    if tw:
        tw.configure(font=CTkFont(size=font_size, family=style))
        frame = tab_frames.get(active_tab_name)
        if frame:
            for child in frame.winfo_children():
                if isinstance(child, CTkTextbox) and child != tw:
                    child.configure(font=CTkFont(size=font_size, family=style))
    font_style_label.configure(text=f"Font Style: {style}")
    font_style_btn.configure(text=f"Font Style: {style}")
    settings["font_style"] = style
    save_settings(settings)
FONT_SIZES = [9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
def set_font_size(size):
    global font_size, settings
    font_size = size
    font_size_label.configure(text=f"Font Size: {size}")
    font_size_btn.configure(text=f"Font Size: {size}")
    tw = get_active_text_widget()
    if tw:
        tw.configure(font=CTkFont(size=size))
        frame = tab_frames.get(active_tab_name)
        if frame:
            for child in frame.winfo_children():
                if isinstance(child, CTkTextbox) and child != tw:
                    child.configure(font=CTkFont(size=size))
    # Save to settings
    settings["font_size"] = size
    save_settings(settings)

def toggle_word_wrap():
    global WORD_WRAP, settings
    if WORD_WRAP == "none":
        WORD_WRAP = "word"
    else:
        WORD_WRAP = "none"
        
    word_wrap_label.configure(text=f"Word Wrap:on" if WORD_WRAP == "word" else "Word Wrap:off")
    word_wrap_btn.configure(text=f"Word Wrap:on" if WORD_WRAP == "word" else "Word Wrap:off")
    for tw in tab_textwidgets.values():
        tw.configure(wrap=WORD_WRAP)
    
    settings["word_wrap"] = WORD_WRAP
    save_settings(settings)


# Tab data structures
tab_frames = {}       # tab_name -> Frame
tab_buttons = {}      # tab_name -> Frame (button container)
tab_textwidgets = {}  # tab_name -> CTkTextbox
tab_file_paths = {}   # tab_name -> file path or None
last_file_snapshots = {}  # tab_name -> last known file content
active_tab_name = None

# ---------- Theme persistence ----------
SETTINGS_FILE = "settings.json"
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                if "theme" not in data:
                    data["theme"] = "dark"
                if "autosave" not in data:
                    data["autosave"] = False
                if "font_size" not in data:
                    data["font_size"] = 15
                if "word_wrap" not in data:
                    data["word_wrap"] = "none"
                if "font_style" not in data:
                    data["font_style"] = "Consolas"
                if "bottom_bar" not in data:
                    data["bottom_bar"] = True
                return data
        except json.JSONDecodeError:
            print("[Settings] Corrupted JSON, loading defaults.")
    return {
        "theme": "dark",
        "autosave": False,
        "font_size": 15,
        "word_wrap": "none",
        "font_style": "Consolas",
        "bottom_bar": True
    }

settings = load_settings()
mode = settings.get("theme", "dark")
autosave = settings.get("autosave", False)
font_size = settings.get("font_size", 15)
WORD_WRAP = settings.get("word_wrap", "none")


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
def auto_save_settings_loop():
    save_settings(settings)             
    root.after(3000, auto_save_settings_loop)  



# ---------- Helper UI-updates ----------
def apply_theme_to_all_widgets():
    # navbar, bottombar, file/edit dropdowns, find/replace bar and all tabs
    navbar.configure(fg_color=nav_color)
    bottombar.configure(fg_color=nav_color)
    file_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    edit_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    position_label.configure(text_color=text_color)
    char_count_label.configure(text_color=text_color)
    switch1.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    undo_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    redo_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    auto_save_label.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    word_wrap_label.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    # icon sticky
    global icon_image, cut_image, copy_image, paste_image, select_all_image
    try:
        image_path = "sun1.png" if mode == "dark" else "sun.png"
        icon_image = CTkImage(Image.open(image_path), size=(20, 20))
        cut_image = CTkImage(Image.open("cut.png" if mode == "dark" else "cut_dark.png"))
        copy_image = CTkImage(Image.open("copy.png" if mode == "dark" else "copy_dark.png"))
        paste_image = CTkImage(Image.open("paste.png" if mode == "dark" else "paste_dark.png"))
        select_all_image = CTkImage(Image.open("select_all.png" if mode == "dark" else "select_all_dark.png"))
    except Exception as e:
        icon_image = None
    switch1.configure(image=icon_image)
    right_click_menu_copy_btn.configure(image=copy_image)
    right_click_menu_cut_btn.configure(image=cut_image)
    right_click_menu_paste_btn.configure(image=paste_image)
    right_click_menu_select_all_btn.configure(image=select_all_image)

    dropdown_frame_file.configure(fg_color=nav_color)
    for child in dropdown_frame_file.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)

    dropdown_frame_edit.configure(fg_color=nav_color)
    for child in dropdown_frame_edit.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)

    find_replace_bar.configure(fg_color=text_area_bg)
    find_entry.configure(fg_color=text_area_bg, text_color=text_color)
    replace_entry.configure(fg_color=text_area_bg, text_color=text_color)
    for child in find_replace_bar.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=text_area_bg, hover_color=hover_color, text_color=text_color)
        if isinstance(child, CTkFrame):
            child.configure(fg_color=text_color)

    # plus button
    if plus_button:
        plus_button.configure(fg_color=text_area_bg, text_color=text_color, hover_color="#888787")
    

    editor_area.configure(fg_color=text_area_bg)
    for child in tab_bar.winfo_children():
        if child != plus_button:
            for btn in child.winfo_children():
                try:
                    btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
                except:
                    pass
    # Update each tab's text widget and tab frames
    tab_canvas.configure(bg=nav_color)
    tab_bar_row.configure(fg_color=nav_color)
    tab_bar_container.configure(fg_color=nav_color)
    tab_bar.configure(fg_color=nav_color)
    for name, textbox in tab_textwidgets.items():
        try:
            textbox.configure(fg_color=text_area_bg, text_color=text_color)
            tab_frames[name].configure(fg_color=text_area_bg)
        except:
            pass
    
   # Update line numbers color
    for name, frame in tab_frames.items():
        for child in frame.winfo_children():
            if isinstance(child, CTkTextbox) and child != tab_textwidgets.get(name):
                try:
                    child.configure(fg_color=text_area_bg)
                except:
                    pass

    #font size and style dropdown
    font_size_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    dropdown_frame_font_size.configure(fg_color=nav_color)
    for child in dropdown_frame_font_size.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    font_size_label.configure(fg_color=nav_color, text_color=text_color)
    font_style_label.configure(fg_color=nav_color, text_color=text_color)
    font_style_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    for child in dropdown_frame_font_style.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    
    #view button
    view_btn.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    dropdown_frame_view.configure(fg_color=nav_color)
    for child in dropdown_frame_view.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)

    #Right-click context menu
    right_click_menu.configure(fg_color=nav_color)
    for child in right_click_menu.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    button_bar.configure(fg_color=nav_color)
    for child in button_bar.winfo_children():
        if isinstance(child, CTkButton):
            child.configure(fg_color=nav_color, hover_color=hover_color, text_color=text_color)
    
# ---------- Theme switch ----------
def switch():
    global mode, nav_color, hover_color, text_color, text_area_bg
    if mode == "light":
        mode = "dark"
        nav_color = "#201F1F"
        hover_color = "#2B2929"
        text_color = "#FFFFFF"
        text_area_bg = "#292727"
    else:
        mode = "light"
        nav_color = "#EEEEEE"
        hover_color = "#DAD8D8"
        text_color = "#000000"
        text_area_bg = "#FFFFFF"

    settings["theme"] = mode
    save_settings(settings)

    set_appearance_mode(mode)
    apply_theme_to_all_widgets()

# ---------- File monitoring ----------
def start_file_monitor():
    check_file_updates()
    root.after(2000, start_file_monitor)  # every 2 seconds

def check_file_updates():
    # Only check for the active tab's file
    if not active_tab_name:
        return
    file_path = tab_file_paths.get(active_tab_name)
    if not file_path:
        return
    if not os.path.exists(file_path):
        # If the file was deleted, close the tab
        close_tab(active_tab_name)
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            new_content = f.read()
    except Exception:
        return

    old_content = last_file_snapshots.get(active_tab_name)
    if old_content is not None and new_content != old_content:
        # Update the textbox content (preserve undo stack? CTkTextbox doesn't expose that easily)
        tw = get_active_text_widget()
        if tw:
            tw.delete("1.0", END)
            tw.insert("1.0", new_content)
    last_file_snapshots[active_tab_name] = new_content

# ---------- Dropdown toggles ----------
def toggle_dropdown_file():
    if dropdown_frame_file.winfo_ismapped():
        dropdown_frame_file.place_forget()
    else:
        dropdown_frame_edit.place_forget()
        x = file_btn.winfo_rootx() - root.winfo_rootx()
        y = navbar.winfo_height()
        dropdown_frame_file.place(x=x, y=y)

def toggle_dropdown_edit():
    if dropdown_frame_edit.winfo_ismapped():
        dropdown_frame_edit.place_forget()
    else:
        dropdown_frame_file.place_forget()
        x = edit_btn.winfo_rootx() - root.winfo_rootx()
        y = navbar.winfo_height()
        dropdown_frame_edit.place(x=x, y=y)

def hide_dropdowns_on_click_mouse(event):
    widget = event.widget

    # Helper function to check if widget is inside a frame/button
    def inside(widget, frame):
        while hasattr(widget, "master") and widget:  # <-- Safe check
            if widget == frame:
                return True
            widget = widget.master
        return False

    # Main dropdowns
    if dropdown_frame_file.winfo_ismapped() and not inside(widget, file_btn) and not inside(widget, dropdown_frame_file):
        dropdown_frame_file.place_forget()
    if dropdown_frame_edit.winfo_ismapped() and not inside(widget, edit_btn) and not inside(widget, dropdown_frame_edit):
        dropdown_frame_edit.place_forget()
    if dropdown_frame_view.winfo_ismapped() and not inside(widget, view_btn) and not inside(widget, dropdown_frame_view):
        dropdown_frame_view.place_forget()

    # Font submenus
    if dropdown_frame_font_size.winfo_ismapped() and not inside(widget, font_size_btn) and not inside(widget, dropdown_frame_font_size):
        dropdown_frame_font_size.place_forget()
    if dropdown_frame_font_style.winfo_ismapped() and not inside(widget, font_style_btn) and not inside(widget, dropdown_frame_font_style):
        dropdown_frame_font_style.place_forget()

    # Right-click context menu
    if right_click_menu.winfo_ismapped() and not inside(widget, right_click_menu):
        right_click_menu.place_forget()

   

# ---------- File operations (adapted for custom tabs) ----------
def new_file():
    # find a new untitled name not used yet
    untitled_count = 1
    while f"Untitled {untitled_count}" in tab_frames:
        untitled_count += 1
    filename = f"Untitled {untitled_count}"
    add_custom_tab(filename)
    tw = tab_textwidgets.get(filename)
    if tw:
        tw.delete("1.0", END)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=FILE_TYPES, title="Open Text File")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
            return
        filename = os.path.basename(file_path)
        # if tab with same name exists, append a suffix
        unique_name = filename
        count = 1
        while unique_name in tab_frames:
            unique_name = f"{filename} ({count})"
            count += 1
        add_custom_tab(unique_name)
        tw = tab_textwidgets[unique_name]
        tw.insert("1.0", content)
        tab_file_paths[unique_name] = file_path
        last_file_snapshots[unique_name] = content
        switch_tab(unique_name)
        start_file_monitor()

def save_file():
    global last_file_snapshots
    tw = get_active_text_widget()
    if not active_tab_name or tw is None:
        return
    file_path = tab_file_paths.get(active_tab_name)
    content = tw.get("1.0", END)
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            last_file_snapshots[active_tab_name] = content
            start_file_monitor()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
    else:
        save_as_file()

def save_as_file():
    tw = get_active_text_widget()
    if not active_tab_name or tw is None:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=FILE_TYPES, title="Save File")
    if not file_path:
        return
    content = tw.get("1.0", END)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")
        return

    filename = os.path.basename(file_path)
    # If tab name equals filename and unique, reuse; otherwise rename tab
    current_name = active_tab_name
    # Close current tab and create a new tab with the filename to simulate 'save as' behavior
    # But prefer not to lose content; create new tab then close old.
    unique_name = filename
    count = 1
    while unique_name in tab_frames:
        unique_name = f"{filename} ({count})"
        count += 1

    add_custom_tab(unique_name)
    new_tw = tab_textwidgets[unique_name]
    new_tw.delete("1.0", END)
    new_tw.insert("1.0", content)
    tab_file_paths[unique_name] = file_path
    last_file_snapshots[unique_name] = content
    switch_tab(unique_name)

    # Close the old tab
    if current_name in tab_frames:
        close_tab(current_name)

    start_file_monitor()

# ---------- Find/Replace ----------
def close_find_replace_bar():
    find_replace_bar.pack_forget()
    tw = get_active_text_widget()
    if tw:
        tw.tag_remove("found", "1.0", END)

def search_text():
    tw = get_active_text_widget()
    if tw is None:
        return
    tw.tag_remove("found", "1.0", END)
    search_term = find_entry.get()
    found = False

    if search_term:
        start_pos = "1.0"
        while True:
            start_pos = tw.search(search_term, start_pos, stopindex=END)
            if not start_pos:
                break
            found = True
            end_pos = f"{start_pos}+{len(search_term)}c"
            tw.tag_add("found", start_pos, end_pos)
            start_pos = end_pos

        if found:
            tw.tag_config("found", background="#FFDD57", foreground="#000000")
        else:
            messagebox.showinfo("Not Found", f"'{search_term}' was not found in the document.")

def replace_text():
    tw = get_active_text_widget()
    if tw is None:
        return
    find_term = find_entry.get()
    replace_term = replace_entry.get()
    if find_term:
        start_pos = "1.0"
        while True:
            start_pos = tw.search(find_term, start_pos, stopindex=END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(find_term)}c"
            tw.delete(start_pos, end_pos)
            tw.insert(start_pos, replace_term)
            start_pos = f"{start_pos}+{len(replace_term)}c"

# ---------- Bottom bar updates ----------
def update_BottomBar(event=None):
    tw = get_active_text_widget()
    if tw:
        try:
            index = tw.index(INSERT)
            line, column = index.split(".")
            position_label.configure(text=f"Ln {line}, Col {int(column)+1}")
        except Exception:
            position_label.configure(text="Ln 1, Col 1")
        content = tw.get("1.0", "end-1c")
        char_count_label.configure(text=f"{len(content)} characters")
    else:
        position_label.configure(text="Ln 1, Col 1")
        char_count_label.configure(text="0 characters")


def show_right_click_menu(event):
    x = event.x_root - root.winfo_rootx()
    y = event.y_root - root.winfo_rooty()

    # Get menu and window sizes
    menu_width = right_click_menu.winfo_reqwidth()
    menu_height = right_click_menu.winfo_reqheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    if x + menu_width > window_width:
        x = max(0, window_width - menu_width - 5)  # 5px margin

    if y + menu_height > window_height:
        y = max(0, window_height - menu_height - 5)

    right_click_menu.place(x=x, y=y)
    right_click_menu.lift()



def hide_right_click_menu(event=None):
    right_click_menu.place_forget()

# ---------- Tab system (custom horizontal tabs) ----------
def switch_tab(tab_name):
    global active_tab_name
    if tab_name not in tab_frames:
        return
    active_tab_name = tab_name

    # Hide all frames
    for name, frame in tab_frames.items():
        frame.pack_forget()
    # Show the active one
    tab_frames[tab_name].pack(fill=BOTH, expand=True)

    # Highlight active tab button
    for name, btn_frame in tab_buttons.items():
        for widget in btn_frame.winfo_children():
            try:
                widget.configure(fg_color=nav_color)
            except:
                pass
    for widget in tab_buttons[tab_name].winfo_children():
        try:
            widget.configure(fg_color=hover_color)
        except:
            pass

    # Update bottom bar and start monitor for this tab
    update_BottomBar()
    start_file_monitor()

    tw = get_active_text_widget()
    if tw:
        tw.unbind("<Button-3>")
        tw.bind("<Button-3>", show_right_click_menu)

def close_tab(tab_name):
    global active_tab_name
    if tab_name not in tab_frames:
        return
    # destroy UI and remove references
    try:
        tab_frames[tab_name].destroy()
    except:
        pass
    try:
        tab_buttons[tab_name].destroy()
    except:
        pass

    tab_frames.pop(tab_name, None)
    tab_buttons.pop(tab_name, None)
    tab_textwidgets.pop(tab_name, None)
    tab_file_paths.pop(tab_name, None)
    last_file_snapshots.pop(tab_name, None)

    # If the closed tab was active, switch to another or create new untitled
    if active_tab_name == tab_name:
        if tab_frames:
            remaining = list(tab_frames.keys())
            switch_tab(remaining[-1])
        else:
            add_custom_tab("Untitled 1")

    update_tab_scrollregion()


#autosave toggle
def toggle_autosave():
    global autosave, settings
    autosave = not autosave
    settings["autosave"] = autosave
    save_settings(settings)
    message = "Autosave enabled" if autosave else "Autosave disabled"
    print(f"{message}")
    auto_save_label.configure(text=f"Autosave: {'On' if autosave else 'Off'}")
    auto_save_btn.configure(text=f"Autosave: {'On' if autosave else 'Off'}")

def auto_save_on_change(tab_name):
    if not autosave:
        return
    tw = tab_textwidgets.get(tab_name)
    file_path = tab_file_paths.get(tab_name)
    if tw and file_path:
        try:
            content = tw.get("1.0", END)
            # Only write if content changed to avoid unnecessary disk writes
            if content != last_file_snapshots.get(tab_name):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                last_file_snapshots[tab_name] = content
        except Exception as e:
            print(f"[Autosave] Could not save {file_path}: {e}")


def add_custom_tab(name="Untitled"):
    global plus_button
    # Ensure unique name
    base = name
    count = 1
    while name in tab_frames:
        name = f"{base} ({count})"
        count += 1

    # Tab button container
    tab_button_frame = CTkFrame(tab_bar, fg_color="transparent",corner_radius=0)
    tab_button_frame.pack(side=LEFT, padx=0)

    tab_btn = CTkButton(
        tab_button_frame, text=name, width=120, height=30,
        fg_color=nav_color, hover_color=hover_color,
        text_color=text_color, corner_radius=5,
        command=lambda n=name: switch_tab(n)
    )
    tab_btn.pack(side=LEFT, padx=0)

    close_btn = CTkButton(
        tab_button_frame, text="✕", width=25, height=30,
        fg_color=nav_color, hover_color="#ff5555",
        text_color=text_color, corner_radius=0,
        command=lambda n=name: close_tab(n)
    )
    close_btn.pack(side=LEFT, padx=(0, 0))
    global tab_buttons
    tab_buttons[name] = tab_button_frame
    # Editor frame
    frame = CTkFrame(editor_area, fg_color=text_area_bg)
    global text_widget
    text_widget = CTkTextbox(
        frame, font=CTkFont(size=font_size), wrap=WORD_WRAP,
        fg_color=text_area_bg, text_color=text_color,
        border_width=0, undo=True
    )
    
    text_widget.pack(side=RIGHT, fill=BOTH, expand=True)

    tab_frames[name] = frame
    tab_textwidgets[name] = text_widget
    tab_file_paths[name] = None
    last_file_snapshots[name] = None

    # Show the new tab
    switch_tab(name)
    tab_btn.bind("<Double-Button-1>", lambda e: rename_tab(name))
    # Keep plus button at end if exists
    if plus_button:
        plus_button.pack_forget()
        plus_button.pack(side=RIGHT, padx=(0, 0))

#session data
def save_session():
    session_data = []

    for tab_name, text_widget in tab_textwidgets.items():
        file_path = tab_file_paths.get(tab_name)

        if file_path:  # Saved file tab
            session_data.append({
                "type": "file",
                "path": file_path
            })
        else:  # Unsaved / Untitled tab
            content = text_widget.get("1.0", "end-1c").strip()
            if content:  # Only save non-empty ones
                session_data.append({
                    "type": "untitled",
                    "content": content
                })

    settings["session"] = session_data
    # Save last active tab
    settings["last_active_tab"] = active_tab_name
    save_settings(settings)


def new_tab():
    count = len(tab_frames) + 1
    add_custom_tab(f"Untitled {count}")

def get_active_text_widget():
    if active_tab_name and active_tab_name in tab_textwidgets:
        return tab_textwidgets[active_tab_name]
    return None

def rename_tab(tab_name):
    file_path = tab_file_paths.get(tab_name)

    if not file_path:
        save_as_file()
        return

    popup = CTkToplevel(root)
    popup.overrideredirect(True)  
    popup.geometry("300x170")
    popup.attributes("-topmost", True)
    popup.grab_set()
    popup.focus_force()
    popup.attributes("-alpha", 1.0)
    try:
        popup.attributes("-transparentcolor", popup.cget("bg"))
    except Exception:
        pass

    # --- Center on root window ---
    popup.update_idletasks()
    popup_width, popup_height = 300, 170
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root_x + (root_width // 2) - (popup_width // 2)
    y = root_y + (root_height // 2) - (popup_height // 2)
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    popup.bind("<Escape>", lambda e: popup.destroy())
    # --- Rounded container frame ---
    container = CTkFrame(popup, corner_radius=20, fg_color=text_area_bg)
    container.pack(expand=True, fill="both", padx=5, pady=5)

    # --- Content ---
    CTkLabel(container, text="Rename Tab", font=CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
    CTkLabel(container, text="Enter new name:", font=CTkFont(size=13)).pack()

    entry = CTkEntry(container, width=200)
    entry.insert(0, tab_name)
    entry.pack(pady=5)
    entry.focus_set()
    entry.bind("<Return>", lambda e: confirm_rename())

    def confirm_rename():
        new_name = entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Name cannot be empty.", parent=popup)
            return
        if new_name in tab_frames and new_name != tab_name:
            messagebox.showerror("Error", "A tab with this name already exists.", parent=popup)
            return

        # Save current content
        content = tab_textwidgets[tab_name].get("1.0", END)
        file_path = tab_file_paths.get(tab_name)
        snapshot = last_file_snapshots.get(tab_name)

        # If file exists, rename it
        if file_path and os.path.exists(file_path):
            dir_path = os.path.dirname(file_path)
            new_path = os.path.join(dir_path, new_name)
            if not os.path.splitext(new_path)[1]:
                new_path += os.path.splitext(file_path)[1]

            if os.path.exists(new_path):
                confirm_overwrite = messagebox.askyesno(
                    "File Exists",
                    f"A file named '{os.path.basename(new_path)}' already exists.\nDo you want to overwrite it?",
                    parent=popup
                )
                if not confirm_overwrite:
                    return
            try:
                os.rename(file_path, new_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename file:\n{e}", parent=popup)
                return
            file_path = new_path

        # Close old tab
        close_tab(tab_name)

        # Add new tab with new name
        add_custom_tab(new_name)
        tab_textwidgets[new_name].delete("1.0", END)
        tab_textwidgets[new_name].insert("1.0", content)
        tab_file_paths[new_name] = file_path
        last_file_snapshots[new_name] = snapshot

        # Switch to new tab
        switch_tab(new_name)

        popup.destroy()



    # --- Buttons ---
    btn_frame = CTkFrame(container, fg_color="transparent")
    btn_frame.pack(pady=10)
    global close_popup
    close_popup = popup.destroy
    CTkButton(btn_frame, text="Rename", width=100, command=confirm_rename).pack(side=LEFT, padx=5)
    CTkButton(btn_frame, text="Cancel", width=100, fg_color="#c21a07",
              hover_color="#a81808", command=close_popup).pack(side=LEFT, padx=5)



# ---------- GUI layout ----------
# window geometry
window_width = 850
window_height = 530
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.minsize(650, 450)
root.resizable(True, True)
try:
    root.iconbitmap("note.ico")
except:
    pass

# Key bindings (some call functions that reference get_active_text_widget())
root.bind("<Escape>", lambda e: find_replace_bar.pack_forget(),add="+")
root.bind("<Control-f>", lambda event: [find_replace_bar.pack(side=RIGHT, padx=1), find_entry.focus_set()])
root.bind("<Control-s>", lambda event: save_file())
root.bind("<Control-Shift-S>", lambda event: save_as_file())
root.bind("<Control-n>", lambda event: new_file())
root.bind("<Control-o>", lambda event: open_file())
root.bind("<Alt-a>", lambda event: switch())
root.bind("<Button-1>", hide_dropdowns_on_click_mouse, add="+")
root.bind("<Button-2>", hide_dropdowns_on_click_mouse, add="+")
root.bind("<Button-3>", hide_dropdowns_on_click_mouse, add="+")
root.bind("<Escape>", hide_dropdowns_on_click_mouse, add="+")

mainframe = CTkFrame(root, corner_radius=0)
mainframe.pack(fill=BOTH, expand=True, padx=0, pady=0)

# Navbar
navbar = CTkFrame(mainframe, height=30, fg_color="#201F1F", corner_radius=0)
navbar.pack(side=TOP, fill=X, padx=0, pady=0)
navbar.pack_propagate(False)

# File button and dropdown
file_btn = CTkButton(navbar, text="File", fg_color="#201F1F", hover_color="#2B2929", text_color="#FFFFFF",
                     font=CTkFont(size=15), width=40, height=30, cursor="hand2", corner_radius=5,
                     anchor=CENTER, command=toggle_dropdown_file)
file_btn.pack(side=LEFT, padx=(5, 5), pady=0)

dropdown_frame_file = CTkFrame(root, fg_color="#201F1F", corner_radius=12, height=120, width=140)
CTkButton(dropdown_frame_file, text="New Tab", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=new_file).pack(fill=X)
CTkButton(dropdown_frame_file, text="Open", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=open_file).pack(fill=X)
CTkButton(dropdown_frame_file, text="Save", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=save_file).pack(fill=X)
CTkButton(dropdown_frame_file, text="Save as", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=save_as_file).pack(fill=X)
CTkButton(dropdown_frame_file, text="Exit", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=root.quit).pack(fill=X)

# Edit button and dropdown
edit_btn = CTkButton(navbar, text="Edit", fg_color="#201F1F", hover_color="#2B2929", text_color="#FFFFFF",
                     font=CTkFont(size=15), width=40, height=30, cursor="hand2", corner_radius=5,
                     anchor=CENTER, command=toggle_dropdown_edit)
edit_btn.pack(side=LEFT, padx=(0, 5), pady=0)

dropdown_frame_edit = CTkFrame(root, fg_color="#201F1F", corner_radius=12, height=80, width=140)
CTkButton(dropdown_frame_edit, text="Undo", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+z")).pack(fill=X)
CTkButton(dropdown_frame_edit, text="Redo", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+y")).pack(fill=X)

CTkFrame(dropdown_frame_edit, height=2, fg_color="#7E7C7C").pack(fill=X, pady=5)
CTkButton(dropdown_frame_edit, text="Select All", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+a")).pack(fill=X)
CTkButton(dropdown_frame_edit, text="Cut", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+x")).pack(fill=X)
CTkButton(dropdown_frame_edit, text="Copy", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+c")).pack(fill=X)
CTkButton(dropdown_frame_edit, text="Paste", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+v")).pack(fill=X)

CTkFrame(dropdown_frame_edit, height=2, fg_color="#7E7C7C").pack(fill=X, pady=5)
CTkButton(dropdown_frame_edit, text="Find/Replace", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: [find_replace_bar.pack(side=RIGHT, padx=1), find_entry.focus_set()]).pack(fill=X)

CTkFrame(dropdown_frame_edit, height=2, fg_color="#7E7C7C").pack(fill=X, pady=5)
CTkButton(dropdown_frame_edit, text="Close Tab", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: close_tab(active_tab_name) if active_tab_name else None).pack(fill=X)
CTkButton(dropdown_frame_edit, text="Rename Tab", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: rename_tab(active_tab_name) if active_tab_name else None).pack(fill=X)

CTkFrame(dropdown_frame_edit, height=2, fg_color="#7E7C7C").pack(fill=X, pady=5)

#view Button

view_btn = CTkButton(navbar, text="View", fg_color="#201F1F", hover_color="#2B2929", text_color="#FFFFFF",
                     font=CTkFont(size=15), width=40, height=30, cursor="hand2", corner_radius=5,
                     anchor=CENTER, command=lambda: toggle_dropdown_view())
view_btn.pack(side=LEFT, padx=(0, 5), pady=0)
dropdown_frame_view = CTkFrame(root, fg_color="#201F1F", corner_radius=12, height=80, width=140)
auto_save_btn = CTkButton(dropdown_frame_view, text=f"Autosave: {'on' if settings['autosave'] else 'off'}", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=toggle_autosave)
auto_save_btn.pack(fill=X)
word_wrap_btn = CTkButton(dropdown_frame_view, text=f"Word Wrap: {'on' if settings['word_wrap'] == 'word' else 'off'}", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=toggle_word_wrap)
word_wrap_btn.pack(fill=X)

def toggle_dropdown_view():
    if dropdown_frame_view.winfo_ismapped():
        dropdown_frame_view.place_forget()
    else:
        x = view_btn.winfo_rootx() - root.winfo_rootx()
        y = navbar.winfo_height()
        dropdown_frame_view.place(x=x, y=y)

#font size submenu
font_size_btn = CTkButton(dropdown_frame_edit, text=f"Font Size: {settings['font_size']}", fg_color=nav_color, hover_color=hover_color, text_color=text_color, anchor="w")
font_size_btn.pack(fill=X)
dropdown_frame_font_size = CTkFrame(root, fg_color="transparent", height=30, width=140)
for size in FONT_SIZES:
    CTkButton(dropdown_frame_font_size, text=str(size), width=80, fg_color=nav_color, font=CTkFont(size=12),
              hover_color=hover_color, text_color=text_color, height=12,
              anchor="w", command=lambda s=size: [set_font_size(s), dropdown_frame_font_size.place_forget()]).pack(fill=X)
def toggle_dropdown_font_size():
    if dropdown_frame_font_style.winfo_ismapped():
        dropdown_frame_font_style.place_forget()
    if dropdown_frame_font_size.winfo_ismapped():
        dropdown_frame_font_size.place_forget()
    else:
        x = font_size_btn.winfo_rootx() - root.winfo_rootx() + font_size_btn.winfo_width()
        y = font_size_btn.winfo_rooty() - root.winfo_rooty()
        dropdown_frame_font_size.place(x=x, y=y)
font_size_btn.configure(command=toggle_dropdown_font_size)
#font size submenu
font_style_btn = CTkButton(dropdown_frame_edit, text=f"Font Style: {settings['font_style']}", fg_color=nav_color, hover_color=hover_color, text_color=text_color, anchor="w")
font_style_btn.pack(fill=X)
dropdown_frame_font_style = CTkFrame(root, fg_color="transparent", height=30, width=140)
for style in FONT_STYLES:
    CTkButton(dropdown_frame_font_style, text=style, width=80, fg_color=nav_color, font=CTkFont(size=12),
              hover_color=hover_color, text_color=text_color, height=12,
              anchor="w", command=lambda s=style: [set_font_style(s), dropdown_frame_font_style.place_forget()]).pack(fill=X)
def toggle_dropdown_font_style():
    if dropdown_frame_font_size.winfo_ismapped():
        dropdown_frame_font_size.place_forget()   
    if dropdown_frame_font_style.winfo_ismapped():
        dropdown_frame_font_style.place_forget()
    else:
        x = font_style_btn.winfo_rootx() - root.winfo_rootx() + font_style_btn.winfo_width()
        y = font_style_btn.winfo_rooty() - root.winfo_rooty()
        dropdown_frame_font_style.place(x=x, y=y)
font_style_btn.configure(command=toggle_dropdown_font_style)

# Theme switch button
settings = load_settings()
set_appearance_mode(settings.get("theme", "dark"))
if settings.get("theme", "dark") == "dark":
    nav_color = "#201F1F"
    hover_color = "#2B2929"
    text_color = "#FFFFFF"
    text_area_bg = "#292727"
else:
    nav_color = "#EEEEEE"
    hover_color = "#DAD8D8"
    text_color = "#000000"
    text_area_bg = "#FFFFFF"

try:
    image_path = "sun1.png" if settings.get("theme", "dark") == "dark" else "sun.png"
    icon_image = CTkImage(Image.open(image_path), size=(20, 20))
except Exception as e:
    icon_image = None

switch1 = CTkButton(navbar, text="", image=icon_image, fg_color=nav_color, text_color=text_color,
                    font=CTkFont(size=12), cursor="hand2", corner_radius=5, anchor=CENTER, width=30, height=30,
                    hover_color=hover_color, command=switch)
switch1.pack(side=RIGHT, padx=(0, 5), pady=0)


# Undo Redo button
redo_btn = CTkButton(navbar, text="↷",fg_color=nav_color, text_color=text_color,
                    font=CTkFont(size=25), cursor="hand2", corner_radius=5, anchor=CENTER, width=30, height=30,
                    hover_color=hover_color, command=lambda:key.press_and_release("ctrl+y"))
redo_btn.pack(side=RIGHT, padx=(0, 15), pady=0)

undo_btn = CTkButton(navbar, text="↶",fg_color=nav_color, text_color=text_color,
                    font=CTkFont(size=25), cursor="hand2", corner_radius=5, anchor=CENTER, width=30, height=30,
                    hover_color=hover_color, command=lambda:key.press_and_release("ctrl+z"))
undo_btn.pack(side=RIGHT, padx=0, pady=0)

# Bottom bar
bottombar = CTkFrame(mainframe, height=25, fg_color=nav_color, corner_radius=0)
if settings.get("bottom_bar", True):
    bottombar.pack(side=BOTTOM, fill=X)


position_label = CTkLabel(bottombar, text="Ln 1, Col 1", text_color=text_color, font=CTkFont(size=11), fg_color="transparent", height=25)
position_label.pack(side=LEFT, padx=(5,5))

separator = CTkFrame(bottombar, width=2, height=25, fg_color="#7E7C7C")
separator.pack(side=LEFT, padx=2, pady=0)

char_count_label = CTkLabel(bottombar, text="0 characters", font=CTkFont(size=11), fg_color="transparent", text_color=text_color, height=25)
char_count_label.pack(side=LEFT, padx=(5,5))

separator = CTkFrame(bottombar, width=2, height=25, fg_color="#7E7C7C")
separator.pack(side=LEFT, padx=(0,5), pady=0)

font_size_label = CTkLabel(bottombar, text=f"Font Size: {font_size}", font=CTkFont(size=11), fg_color="transparent", text_color=text_color, height=25)
font_size_label.pack(side=LEFT, padx=(0,5))

separator = CTkFrame(bottombar, width=2, height=25, fg_color="#7E7C7C")
separator.pack(side=LEFT, padx=(0,5), pady=0)

font_style_label = CTkLabel(bottombar, text=f"Font Style: {settings.get('font_style', 'Arial')}", font=CTkFont(size=11), fg_color=nav_color, text_color=text_color, height=25)
font_style_label.pack(side=LEFT, padx=(0,5))

separator = CTkFrame(bottombar, width=2, height=25, fg_color="#7E7C7C")
separator.pack(side=LEFT, padx=(0,5), pady=0)

word_wrap_label = CTkButton(bottombar, text=f"Word Wrap: {'On' if WORD_WRAP == 'word' else 'Off'}", font=CTkFont(size=11), fg_color=nav_color, text_color=text_color, height=25,width= 40, hover_color=hover_color, command=toggle_word_wrap)
word_wrap_label.pack(side=RIGHT, padx=(0,5))

separator = CTkFrame(bottombar, width=2, height=25, fg_color="#7E7C7C")
separator.pack(side=RIGHT, padx=(0,5), pady=0)

auto_save_label = CTkButton(bottombar, text=f"Autosave: {'On' if autosave else 'Off'}", font=CTkFont(size=11), fg_color=nav_color, text_color=text_color, height=25, width =40, hover_color=hover_color, command=toggle_autosave)
auto_save_label.pack(side=RIGHT, padx=(0,5))

separator = CTkFrame(bottombar, width=2, height=25, fg_color="#7E7C7C")
separator.pack(side=RIGHT, padx=(0,5), pady=0)

def bottom_bar_visibility():
    if settings['bottom_bar']:
        settings['bottom_bar'] = False
        bottombar.pack_forget()
    else:
        settings['bottom_bar'] = True
        bottombar.pack(side=BOTTOM, fill=X)
    save_settings(settings)
    bottom_bar_visibility_btn.configure(text=f"Bottom Bar: {'on' if settings['bottom_bar'] else 'off'}")

bottom_bar_visibility_btn = CTkButton(dropdown_frame_view, text=f"Bottom Bar: {'on' if settings['bottom_bar'] else 'off'}", width=140, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=bottom_bar_visibility)
bottom_bar_visibility_btn.pack(fill=X)

# --- Tab Bar Container ---
tab_bar_container = CTkFrame(mainframe, height=35, fg_color=nav_color, corner_radius=0)
tab_bar_container.pack(side=TOP, fill=X)

# --- Frame for horizontal layout (canvas + plus) ---
tab_bar_row = CTkFrame(tab_bar_container, fg_color=nav_color)
tab_bar_row.pack(side=TOP, fill=X)

# --- Canvas for scrolling tabs ---
tab_canvas = CTkCanvas(tab_bar_row, height=35, bg=nav_color, highlightthickness=0, bd=0)
tab_canvas.pack(side=LEFT, fill=X, expand=True)

# --- Frame inside canvas to hold tab buttons ---
tab_bar = CTkFrame(tab_canvas, fg_color=nav_color)
tab_window = tab_canvas.create_window((0, 0), window=tab_bar, anchor="nw")

# --- Plus button (fixed, same line) ---
plus_button = CTkButton(
    tab_bar_row, text="➕", width=40, height=30,
    fg_color=text_area_bg, hover_color="#666",
    text_color=text_color, corner_radius=4,
    command=new_tab
)
plus_button.pack(side=RIGHT, padx=(2, 4))

# --- Scrollbar (appears only when needed) ---
tab_scrollbar = CTkScrollbar(tab_bar_container, orientation="horizontal", command=tab_canvas.xview, height=10)
tab_canvas.configure(xscrollcommand=tab_scrollbar.set)
tab_scrollbar.pack_forget()


# --- Update scroll region and scrollbar visibility ---
def update_tab_scrollregion(event=None):
    tab_bar.update_idletasks()

    # total width of tabs
    bar_width = tab_bar.winfo_reqwidth()
    # available width (excluding plus button)
    available_width = tab_canvas.winfo_width()

    # adjust scroll region
    tab_canvas.configure(scrollregion=tab_canvas.bbox("all"))

    # show or hide scrollbar dynamically
    if bar_width <= available_width:
        tab_scrollbar.pack_forget()
    else:
        tab_scrollbar.pack(side=BOTTOM, fill=X)

# Bind updates
tab_bar.bind("<Configure>", update_tab_scrollregion)
tab_canvas.bind("<Configure>", update_tab_scrollregion)



# editor area
editor_area = CTkFrame(mainframe, fg_color=text_area_bg)
editor_area.pack(side=TOP, fill=BOTH, expand=True)


# initial tab
add_custom_tab("Untitled 1")

# ----------------- Floating Find/Replace Bar -----------------
find_replace_bar = CTkFrame(editor_area, fg_color=text_area_bg, height=35, corner_radius=8, border_width=1, border_color=hover_color)
find_replace_bar.place_forget()  # initially hidden

# Find entry
find_entry = CTkEntry(find_replace_bar, placeholder_text="Find...", width=130, height=25, fg_color=text_area_bg, text_color=text_color, border_width=0, corner_radius=0)
find_entry.pack(side=LEFT, padx=(8, 6), pady=4)
find_entry.bind("<Return>", lambda e: search_text())

# Separator
CTkFrame(find_replace_bar, width=2, height=25, fg_color=text_color).pack(side=LEFT, padx=(0, 6), pady=4)

# 
# Replace entry
replace_entry = CTkEntry(find_replace_bar, placeholder_text="Replace with...", width=130, height=25, fg_color=text_area_bg, text_color=text_color, border_width=0, corner_radius=0)
replace_entry.pack(side=LEFT, padx=(6, 4), pady=4)

replace_entry.bind("<Return>", lambda e: replace_text())

# Replace button
CTkButton(find_replace_bar, text="↻", width=30, height=24, font=CTkFont(size=12),
          command=lambda: replace_text(), fg_color=text_area_bg, hover_color=hover_color, text_color=text_color, corner_radius=0).pack(side=LEFT, padx=(0, 4), pady=4)

# Separator
CTkFrame(find_replace_bar, width=2, height=25, fg_color=text_color).pack(side=LEFT, padx=(0, 6), pady=4)

# Close button
CTkButton(find_replace_bar, text="✖️", width=24, height=24, font=CTkFont(size=12),
          command=lambda: find_replace_bar.pack_forget(), fg_color="#da4f3f", hover_color=hover_color, text_color=text_color, corner_radius=0).pack(side=LEFT, padx=(0, 8), pady=4)

# ----------------- Floating / Draggable behavior -----------------
def start_move(event):
    find_replace_bar.startX = event.x
    find_replace_bar.startY = event.y

def on_move(event):
    x = find_replace_bar.winfo_x() + (event.x - find_replace_bar.startX)
    y = find_replace_bar.winfo_y() + (event.y - find_replace_bar.startY)
    find_replace_bar.place(x=x, y=y)

find_replace_bar.bind("<Button-1>", start_move)
find_replace_bar.bind("<B1-Motion>", on_move)

# ----------------- Show function -----------------
def show_find_replace_bar():
    find_replace_bar.place(x=10, y=10, width=400, height=35)
    find_entry.focus_set()



# Right-click context menu
theme = settings.get("theme", "dark") 
cut_image = CTkImage(Image.open("cut.png" if theme == "dark" else "cut_dark.png"))
copy_image = CTkImage(Image.open("copy.png" if theme == "dark" else "copy_dark.png"))
paste_image = CTkImage(Image.open("paste.png" if theme == "dark" else "paste_dark.png"))
select_all_image = CTkImage(Image.open("select_all.png" if theme == "dark" else "select_all_dark.png"))

# right-click menu frame
right_click_menu = CTkFrame(root, fg_color=nav_color, corner_radius=6, height=80, width=245, border_width=1, border_color=hover_color)
right_click_menu.place_forget()

# Horizontal button bar 
button_bar = CTkFrame(right_click_menu, fg_color="transparent")
button_bar.pack(side=TOP, fill=X)

right_click_menu_cut_btn = CTkButton(button_bar, text="Cut", image=cut_image, compound="top", width=60,
    fg_color=nav_color, hover_color=hover_color, text_color=text_color,
    command=lambda: key.press_and_release("Control+x"))
right_click_menu_cut_btn.pack(side=LEFT, padx=0)

CTkFrame(button_bar, width=2, height=30, fg_color="#7E7C7C").pack(side=LEFT, padx=1)

right_click_menu_copy_btn = CTkButton(button_bar, text="Copy", image=copy_image, compound="top", width=60,
    fg_color=nav_color, hover_color=hover_color, text_color=text_color,
    command=lambda: key.press_and_release("Control+c"))
right_click_menu_copy_btn.pack(side=LEFT, padx=0)

CTkFrame(button_bar, width=2, height=30, fg_color="#7E7C7C").pack(side=LEFT, padx=1)

right_click_menu_paste_btn = CTkButton(button_bar, text="Paste", image=paste_image, compound="top", width=60,
    fg_color=nav_color, hover_color=hover_color, text_color=text_color,
    command=lambda: key.press_and_release("Control+v"))
right_click_menu_paste_btn.pack(side=LEFT, padx=0)

CTkFrame(button_bar, width=2, height=30, fg_color="#7E7C7C").pack(side=LEFT, padx=1)

right_click_menu_select_all_btn = CTkButton(button_bar, text="Select All", image=select_all_image, compound="top", width=60,
    fg_color=nav_color, hover_color=hover_color, text_color=text_color,
    command=lambda: key.press_and_release("Control+a"))
right_click_menu_select_all_btn.pack(side=LEFT, padx=0)


CTkButton(right_click_menu, text="Open", width=245, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=open_file).pack(fill=X, side=BOTTOM)
CTkButton(right_click_menu, text="New Tab", width=245, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=new_file).pack(fill=X, side=BOTTOM)
CTkButton(right_click_menu, text="Save", width=245, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=save_file).pack(fill=X, side=BOTTOM)
CTkFrame(right_click_menu, width=245, height=2, fg_color="#7E7C7C").pack(side=BOTTOM, pady=2, fill=X)
CTkButton(right_click_menu, text="Find/Replace", width=245, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: [find_replace_bar.pack(side=RIGHT, padx=1), find_entry.focus_set()]).pack(fill=X, side=BOTTOM)
CTkFrame(right_click_menu, width=245, height=2, fg_color="#7E7C7C").pack(side=BOTTOM, pady=2, fill=X)
CTkButton(right_click_menu, text="Redo", width=245, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+y")).pack(fill=X, side=BOTTOM)
CTkButton(right_click_menu, text="Undo", width=245, fg_color=nav_color, hover_color=hover_color, text_color=text_color,
          anchor="w", command=lambda: key.press_and_release("Control+z")).pack(fill=X, side=BOTTOM)

CTkFrame(right_click_menu, height=2, fg_color="#7E7C7C").pack(side=BOTTOM, pady=2, fill=X)



root.bind("<Button-1>", hide_right_click_menu, add="+")  
root.bind("<Button-2>", hide_right_click_menu, add="+")   
root.bind("<Escape>", hide_right_click_menu, add="+")

# Kick off monitor and theme application
apply_theme_to_all_widgets()
start_file_monitor()
save_settings(settings)


#session restore
def restore_session():
    session_data = settings.get("session", [])
    if not session_data:
        add_custom_tab() 
        return

    restored_tab_names = []

    for item in session_data:
        if item["type"] == "file":
            path = item["path"]
            if os.path.exists(path):
                name = os.path.basename(path)
                add_custom_tab(name)
                tab_textwidgets[name].insert("1.0", open(path, "r", encoding="utf-8").read())
                tab_file_paths[name] = path
                restored_tab_names.append(name)
        elif item["type"] == "untitled":
            name = "Untitled"

            count = 1
            while name in tab_textwidgets:
                name = f"Untitled ({count})"
                count += 1
            add_custom_tab(name)
            tab_textwidgets[name].insert("1.0", item["content"])
            restored_tab_names.append(name)

    # Restore the last active tab
    last_active = settings.get("last_active_tab")
    if last_active in restored_tab_names:
        switch_tab(last_active)
    else:
        switch_tab(restored_tab_names[0])

restore_session()

def on_exit():
    save_session()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
