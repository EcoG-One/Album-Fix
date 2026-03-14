# -*- coding: utf-8 -*-

import csv
import os
import re
import shutil
import threading
import winsound
from tkinter import *
from tkinter import Text, ttk
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.simpledialog import askinteger
from tkinter.ttk import Progressbar
from subprocess import call
from typing import Any, Union
import tkinter as tk
import taglib
import darkdetect as darkdetect
import pandas as pd
import xlsxwriter
import hashlib
import time
import librosa
from dotenv import load_dotenv



def darkstyle(root):
    ''' Return a dark style to the window'''
    style = ttk.Style(root)
    root.tk.call('source', 'azure dark/azure dark.tcl')
    style.theme_use('azure')
    style.configure("Accentbutton", foreground='white')
    style.configure("Togglebutton", foreground='white')
    return style


def create_beutify_file():
    if not os.path.exists(os.path.join(os.getenv('LOCALAPPDATA'), 'beautify.csv')):
        with open(os.path.join(os.getenv('LOCALAPPDATA'), 'beautify.csv'), 'w', encoding="utf-8",
                  newline='') as csvfile:
            fieldnames = ['Old_Name', 'New_Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'Old_Name': "Cd", 'New_Name': "CD"})
            writer.writerow({'Old_Name': "A - Ha", 'New_Name': "A-Ha"})
            writer.writerow({'Old_Name': "Abba ", 'New_Name': "ABBA "})
            writer.writerow({'Old_Name': "Ac - Dc", 'New_Name': "AC-DC"})
            writer.writerow({'Old_Name': "Atb ", 'New_Name': "ATB "})
            writer.writerow({'Old_Name': "B - 52'S", 'New_Name': "B-52's"})
            writer.writerow({'Old_Name': "Cc", 'New_Name': "cc"})
            writer.writerow({'Old_Name': "Ep ", 'New_Name': "EP "})
            writer.writerow({'Old_Name': "Ii", 'New_Name': "II"})
            writer.writerow({'Old_Name': "ii", 'New_Name': "II"})
            writer.writerow({'Old_Name': "iii", 'New_Name': "III"})
            writer.writerow({'Old_Name': "Iv ", 'New_Name': "IV "})
            writer.writerow({'Old_Name': "Ix ", 'New_Name': "IX "})
            writer.writerow({'Old_Name': "Lp ", 'New_Name': "LP "})
            writer.writerow({'Old_Name': "Mfsl", 'New_Name': "MFSL"})
            writer.writerow({'Old_Name': "Ost", 'New_Name': "OST"})
            writer.writerow({'Old_Name': "Sacd", 'New_Name': "SACD"})
            writer.writerow({'Old_Name': "Udcd", 'New_Name': "UDCD"})
            writer.writerow({'Old_Name': "Uk ", 'New_Name': "UK "})
            writer.writerow({'Old_Name': "Usa", 'New_Name': "USA"})
            writer.writerow({'Old_Name': "Vi ", 'New_Name': "VI "})
            writer.writerow({'Old_Name': "Zz", 'New_Name': "ZZ"})
            writer.writerow({'Old_Name': "'S", 'New_Name': "'s"})


class FixEm:
    def __init__(self, _root):
        self.__helpScrollBar = None
        self.__fr = None
        self.__help_text = None
        self.top3 = None
        self.bar_thread = None
        self.list_type = 'quick'
        self.__root = _root
        self.main_frame = Frame(self.__root)
        self.wizard_on = False
        # default window width and height
        self.__rootWidth = self.__root.winfo_screenwidth() / 2
        self.__rootHeight = self.__root.winfo_screenheight() / 2  # TODO
        '''if darkdetect.isDark():
            self.__rootTextArea = Text(self.__root, wrap="none", undo=True, background="#333333", foreground='#ffffff')
        else:'''
        self.__rootTextArea = Text(self.main_frame, wrap="none", undo=True, background='white', foreground='black',
                                   font='TkFixedFont', padx=2)
        self.__rootMenuBar = Menu(self.__root)
        self.__rootFileMenu = Menu(self.__rootMenuBar, tearoff=0)
        self.__rootRenameMenu = Menu(self.__rootMenuBar, tearoff=0)
        self.__rootEditMenu = Menu(self.__rootMenuBar, tearoff=0)
        self.__rootToolsMenu = Menu(self.__rootMenuBar, tearoff=0)
        self.__rootHelpMenu = Menu(self.__rootMenuBar, tearoff=0)

        # Add scrollbar and statusbar
        self.__rootScrollBar = Scrollbar(self.main_frame, cursor='arrow')
        self.__rootScrollBar2 = Scrollbar(self.main_frame, orient='horizontal', cursor='arrow')
        self.context1 = Menu(self.__rootTextArea, tearoff=0)
        self.context1.add_command(label='Cut', command=self.__cut)
        self.context1.add_command(label='Copy', command=self.__copy)
        self.context1.add_command(label='Paste', command=self.__paste)
        self.context1.add_command(label='Undo', command=self.__edit_undo)
        self.context1.add_command(label='Redo', command=self.__edit_redo)
        if self.__root.tk.call('tk', 'windowingsystem') == 'aqua':
            self.__rootTextArea.bind('<2>', self.post1)
        else:
            self.__rootTextArea.bind('<3>', self.post1)

        # Create the status bar at the bottom
        self.status_bar = tk.Frame(self.main_frame, bd=1,
                              relief=tk.SUNKEN)  # Use a Frame for better appearance
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_str = "Welcome"
        self.status_label = Label(self.status_bar, text=self.status_str, relief=SUNKEN, anchor="w")
        self.status_label.pack(side=tk.LEFT)
        __file = None

        self.__my_choice: str = "make_list"
        self.__final_lista: list[dict[str, Union[str, Any]]] = None
        self.__rootPath: str = None

        # Set icon
        icon = os.path.join("images", "List-Icon.ico")
        try:
            self.__root.wm_iconbitmap(bitmap=icon)
        except:
            pass

        # Set the window text
        self.__root.title("EcoG's Fix'em")

        # Center the window
        screen_width = self.__root.winfo_screenwidth()
        screen_height = self.__root.winfo_screenheight()

        # For left-align
        self.left = (screen_width / 4)

        # For right-align
        self.top = (screen_height / 4)

        # For top and bottom
        self.__root.geometry('%dx%d+%d+%d' % (self.__rootWidth,
                                              self.__rootHeight,
                                              self.left, self.top))

        # Make the textarea auto resizable
        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(0, weight=1)

        # Create a new rename list
        self.__rootFileMenu.add_command(label="New Rename List",
                                        command=self.__new_rename_list)
        # Open an existing rename list
        self.__rootFileMenu.add_command(label="Open Rename List",
                                        command=self.__open_rename_list)
        # Save current rename list
        self.__rootFileMenu.add_command(label="Save Rename List",
                                        command=self.__save_rename_list)

        # Create a line in the dialog
        self.__rootFileMenu.add_separator()
        self.__rootFileMenu.add_command(label="Exit",
                                        command=self.__quit_application)

        self.__rootMenuBar.add_cascade(label="File",
                                       menu=self.__rootFileMenu)

        # Wizard
        self.__rootRenameMenu.add_command(label="Rename Wizard",
                                          command=self.__wizard)

        # Rename from an existing rename list
        self.__rootRenameMenu.add_command(label="Rename NOW!",
                                          command=self.__rename_now)

        # Rename from an existing rename list
        self.__rootRenameMenu.add_command(label="Rename From List",
                                          command=self.__rename_from_list)
        # Direct Rename
        self.__rootRenameMenu.add_command(label="Rename Without List",
                                          command=self.__rename)
        # Undo
        self.__rootRenameMenu.add_command(label="Undo Last Rename",
                                          command=self.__undo)
        self.__rootRenameMenu.add_separator()
        # Add Rename words
        self.__rootRenameMenu.add_command(label="Words to Rename",
                                          command=self.RenameDialog)

        self.__rootMenuBar.add_cascade(label="Rename",
                                       menu=self.__rootRenameMenu)

        # cut text from the list
        self.__rootEditMenu.add_command(label="Cut",
                                        command=self.__cut)

        # copy text from the list
        self.__rootEditMenu.add_command(label="Copy",
                                        command=self.__copy)

        # paste text to the list
        self.__rootEditMenu.add_command(label="Paste",
                                        command=self.__paste)

        # Undo Edit
        self.__rootEditMenu.add_command(label="Undo",
                                        command=self.__edit_undo)

        # Redo Edit
        self.__rootEditMenu.add_command(label="Redo",
                                        command=self.__edit_redo)

        # edit rename list
        self.__rootMenuBar.add_cascade(label="Edit",
                                       menu=self.__rootEditMenu)
        # remove Duplicates
        self.__rootToolsMenu.add_command(label="Remove Duplicates",
                                         command=self.remove_duplicate_audio)
        # Measure Loudness
        self.__rootToolsMenu.add_command(label="Measure Loudness",
                                         command=self.loudness)
        # Create Artist Folders and move album folders to artist folders
        self.__rootToolsMenu.add_command(label="Create Artist Folders",
                                         command=self.create_artist_files)

        # move all artist folders to ABC folders
        self.__rootToolsMenu.add_command(label="Move to ABC",
                                         command=self.__abc_open_folder)

        # clean up MQA folders
        self.__rootToolsMenu.add_command(label="MQA Tag Restore",
                                         command=self.__mqa_restore)

        # clean up MQA folders
        self.__rootToolsMenu.add_command(label="Fix MQA",
                                         command=self.__mqa_fix)

        # Extra Functions
        self.__rootMenuBar.add_cascade(label="Tools",
                                       menu=self.__rootToolsMenu)

        self.__rootHelpMenu.add_command(label="Instructions",
                                        command=self.instructions)

        self.__rootHelpMenu.add_command(label="About Fix'em All",
                                        command=self.__show_about)
        self.__rootMenuBar.add_cascade(label="Help",
                                       menu=self.__rootHelpMenu)

        self.__root.config(menu=self.__rootMenuBar)

        # Scrollbar will adjust automatically according to the content
        self.__rootScrollBar.config(command=self.__rootTextArea.yview)
        self.__rootTextArea.config(yscrollcommand=self.__rootScrollBar.set)
        self.__rootScrollBar2.config(command=self.__rootTextArea.xview)
        self.__rootTextArea.config(xscrollcommand=self.__rootScrollBar2.set)

        # Search
        self.top_f = tk.Frame()
        self.top_f.pack(fill='x', padx=2)
        self.term = tk.Entry(self.top_f, bg='lightblue', width=int(self.__rootWidth / 12))
        # self.term.pack(side='right', expand=0, fill='x')
        self.term_label = tk.Label(self.top_f, text='Search:')
        self.term.bind('<Return>', self.search)
        self.wizard_Button = tk.Button(self.top_f, bg='lightgrey', fg='black', text="Rename Wizard",
                                       command=self.__wizard)
        self.wizard_Button.pack(side='left', expand=0, fill='x')
        self.main_frame.pack(expand=True, fill='both')
        self.__rootTextArea.tag_configure('found', background='green', foreground='red')

    def __wizard(self):
        if self.wizard_on is True:
            return
        self.wizard_on = True
        self.wiz_top = tk.Toplevel()
        self.wiz_top.geometry('%dx%d+%d+%d' % (self.__rootWidth / 2,
                                               self.__rootHeight / 2,
                                               self.left * 2.3, self.top / 2))
        self.__wiz = tk.Frame(self.wiz_top)
        self.__wiz.pack(expand=True, fill='both')
        self.wiz_top.focus_set()

        self.current_step = None
        self.steps = [self.Step1(self.__wiz), self.Step2(self.__wiz), self.Step3(self.__wiz), self.Step4(self.__wiz)]

        self.button_frame = tk.Frame(self.__wiz, bd=1, relief="raised")
        self.content_frame = tk.Frame(self.__wiz)

        self.next_button = tk.Button(self.button_frame, text="Next >>", command=self.next)
        self.finish_button = tk.Button(self.button_frame, text="Finish", command=self.finish)

        self.button_frame.pack(side="bottom", fill="x")
        self.content_frame.pack(side="top", fill="both", expand=True)
        self.wiz_top.protocol("WM_DELETE_WINDOW", self.finish)
        self.show_step(0)

    def show_step(self, step):

        if self.current_step is not None:
            # remove current step
            current_step = self.steps[self.current_step]
            current_step.pack_forget()

        self.current_step = step

        new_step = self.steps[step]
        new_step.pack(fill="both", expand=True)

        if step == 0:
            # first step
            self.wiz_top.title('Welcome')
            self.next_button.pack(side="right")
            self.finish_button.pack_forget()
            self.__wiz.focus()
        elif step == 1:
            self.wiz_top.title('Step 1')
            self.next_button.pack_forget()
            self.__wiz.focus()
            self.list_type = 'quick'
            self.__new_list()
            self.wiz_top.deiconify()
            if self.__rootPath is not None and self.__final_lista is not None:
                self.next()
            else:
                self.finish()
                return
        elif step == 2:
            self.wiz_top.title('Step 2')
            self.next_button.pack(side="right")
            self.__wiz.focus()
        elif step == 3:
            self.wiz_top.iconify()
            self.__rename_now()
            self.wiz_top.deiconify()
            try:
                winsound.MessageBeep()
            except RuntimeError as error:
                self.__write_error_log(error)
            finally:
                pass
            self.wiz_top.title('Congratulations!')
            self.next_button.pack_forget()
            self.finish_button.pack(side="right")
            self.__wiz.focus()
        elif step == 4:
            # last step
            self.__wiz.focus().focus()
        else:
            self.finish()

    def next(self):
        self.show_step(self.current_step + 1)

    def finish(self):
        self.wizard_on = False
        self.wiz_top.destroy()
        self.wiz_top.update()

    class Step1(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            header = tk.Label(self, text="Welcome to the Rename Wizard", bd=2, relief="groove")
            header.pack(side="top", fill="x")
            s1_txt = '''           
    Together we will rename your album folders* 
    in two easy steps
    First step is to find your albums and create a
    RENAME LIST
    Press Next to do so


    *The rename pattern is:
    Date. Album Name Additional Info

            '''
            step1_text = tk.Label(self, text=s1_txt, bd=2, relief="groove", fg='black', bg='lightgrey')
            step1_text.pack()

    class Step2(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            header = tk.Label(self, text="Step 1. Choose your albums Folder", bd=2, relief="groove")
            header.pack(side="top", fill="x")
            s2_txt = '''
Please Select the Folder containing 
your Albums and press Select Folder

'''
            step2_text = tk.Label(self, text=s2_txt, bd=2, relief="groove", fg='black', bg='lightgrey')
            step2_text.pack()

    class Step3(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            header = tk.Label(self, text="Step 2.Check and Correct your RENAME LIST", bd=2, relief="groove")
            header.pack(side="top", fill="x")
            s3_txt = '''
            On the middle colon, (named Old_Name), 
you see your album folders names as they are now
On the right colon, (named New_Name),  
you see your album folders names as they will be 
after the RENAME procedure
Feel free to edit the New Names as you like and
when you finish Press Next for the RENAME to start
'''
            step3_text = tk.Label(self, text=s3_txt, bd=2, relief="groove", fg='black', bg='lightgrey')
            step3_text.pack()

    class Step4(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)

            header = tk.Label(self, text="Congratulations!", bd=2, relief="groove")
            header.pack(side="top", fill="x")
            s4_txt = '''
You just completed renaming your album folders
Please press Fnish to close this window


(If any Errors have occurred
 an Error List will pop-up)'''
            step4_text = tk.Label(self, text=s4_txt, bd=2, relief="groove", fg='black', bg='lightgrey')
            step4_text.pack()

    def post1(self, event):  # cascade menu
        self.context1.post(event.x_root, event.y_root)

    def __write_error_log(self, error):
        if self.list_type == 'slow':
            showerror(title='Error!', message=str(error))
        if self.__rootPath:
            self.error_log = open(os.path.join(self.__rootPath, "errorlog.txt"), "a", encoding='utf-8')
            self.error_log.write(str(error) + "\n")
            self.error_log.close()

    def __quit_application(self):
        if self.__rootTextArea.edit_modified():
            self.__MsgBox = tk.messagebox.askquestion('Save List?', 'Rename List has changed. Do You Want to Save It?',
                                                      icon='warning')
            if self.__MsgBox == 'yes':
                self.__save_rename_list()
        self.__root.destroy()

    def __mqa_restore(self):
        try:
            retcode = call('MQATagRestorer.exe', shell=True)
            '''   if retcode < 0:
                print("Child was terminated by signal", -retcode)
            else:
                print("Child returned", retcode) '''
        except OSError as e:
            self.__write_error_log(e)

    def instructions(self):
        self.top3 = tk.Toplevel()
        self.top3.geometry('%dx%d+%d+%d' % (self.__rootWidth * 1.2,
                                            self.__rootHeight - 10,
                                            self.left + 20, self.top - 20))
        self.top3.title("Instructions...")
        self.top3.grab_set()
        info_text = """BRIEF INSTRUCTIONS
The main program's function is to uniformly format the folder name of each Album.
The formatting it attempts to do is unter this pattern:
Release Date. Album Name. Further information, if any. e.g.:
1978. Bloody Tourists (1996)
(where 1996 is the re-release date)

The quick and easy way to apply the formating is by pressing the <Rename Wizard> button, top left.

Alternatively, formatting can be done from the <Rename> menu, either via a list (submenu <Rename from List>), or directly (submenu <Direct Rename> or <Rename Without List>).
To format via a list, we must first create the list, from the <New Rename List> submenu or load an existing one, from the <Open New Rename List> submenu.
From <New Rename List> we select the directory containing the albums we want to format.
The program searches all subdirectories of the directory we selected and finds the folders containing audio files, (FLAC, mp3, m4a, ogg etc.), considering that the folders contain albums.
The list creation can either be automatic or manual; (the selection is made from the relevant window that appears).
If you select <New Rename List>, the program creates an Excel sheet (and a similar CSV text file) listing the current Albums names and how these names the application suggests they should be.
If the program's suggestions do not satisfy you, you can intervene in Excel and make any changes you want and then load it into the program and proceed with the renaming.
If you prefer, you can make the changes directly in the program's built-in editor, which automatically loads the list from the CSV, as soon as it is created.
ATTENTION: Changes made in the built-in Editor are not saved in Excel, but only in CSV. And of course, changes you make in Excel are not saved in CSV - only in Excel. So either you will work on your changes in Excel, (and then load it into the program), or in the program's editor.
Finally, from the <Rename Now> submenu you perform the rename, (according to the list loaded into the Editor).
Alternatively, from the <Rename from List> submenu, the rename is done directly from an existing list, (Excel or CSV) without the possibility of further editing in the Editor. (Any editing must have been done before the list was loaded)
If you regret it, there is the <Undo Last Rename> submenu. If you want to restore an older rename you made, simply swap the Old_Name and New_Name columns in the Rename_List file created in the root folder where you made the changes and load the list from <Rename from List>.

The formatting mechanism is as follows:
Initially, the program scans the album names to find dates. If it finds one, it considers that this is its release date (it is common practice for torrenters to write the release date in the name of an album's folder). If it finds more than one date (usually the second is that of the remaster) it asks you which one you want, suggesting the oldest one. (In automatic mode it does not ask, but selects the oldest date itself). If it does not find a date in the folder name, it looks for a date in the metadata of the album's songs. If it doesn't find it there either, it calls the Spotify database and pulls the information from there. Thus, it creates, not only the release date, but also all the metadata that is missing from the album.
In addition, it cleans the folder names from torrent garbage (spaces, underscores, etc.).

The program has a list of words that it must delete or change in order to eliminate the garbage, but the user can also add or remove words from the <Words to Rename> submenu of the <Rename> menu.
In the list that appears, you add words that you want to change, while you remove or change words by right-clicking. In the <Change> field, enter the word you want to change and in the <To> field, the word that will replace it and then click <Submit> to add the word to the list. When you finish entering words to change or delete from the album names, click <Close> to save them and close the window. If you want a word to be deleted from the album names, simply leave the <To> field blank.

Other Tools:
From the <Move to ABC> submenu of the <Tools> menu, the program groups all albums into folders alphabetically (A, B, C, D, E, ....Z), based on the first letter of the artist's name, then by artist and finally by album. The procedure for doing this is as follows: First, it scans the root folder you choose, finds the album folders and creates a folder for each artist, into which it transfers all their albums, then it gathers all the artist folders with the same first letter in their name into the folders it creates from this first letter (A, B, C...).
If you have an MQA album, with <MQA Tag Restorer> (always in the <Tools> menu), you create the Tags, the name and the structure of files and folders, so that they can be played on consumer players, while from <Fix MQA>, in the <Tools> menu, the program deletes the garbage and duplicate files created by <MQA Tag Restorer>.        
        
ΣΥΝΤΟΜΕΣ ΟΔΗΓΙΕΣ
Βασική δουλειά του προγράμματος είναι να μορφοποιήσει ομοιόμορφα το όνομα φακέλου του κάθε Άλμπουμ. 
Η μορφοποίηση που επιχειρεί να κάνει είναι της μορφής:
 Χρονολογία Έκδοσης. Όνομα άλμπουμ. Περαιτέρω πληροφορίες, αν υπάρχουν. π.χ.:
 1978. Bloody Tourists (1996)
(όπου το 1996 είναι η ημερομηνία επανακυκλοφορίας)

Ο γρήγορος και εύκολος τρόπος μορφοποίησης είναι πατώντας το κουμπί <Rename Wizard>, επάνω αριστερά.

Εναλλακτικά, η μορφοποίηση γίνεται από το μενού <Rename>, είτε μέσω λίστας, (υπομενού <Rename from List>), είτε κατ’ ευθείαν (υπομενού <Direct Rename> ή <Rename Without List>).  
Για να γίνει η μορφοποίηση μέσω λίστας, πρέπει πρώτα να δημιουργήσουμε την λίστα, από το υπομενού <New Rename List> ή να φορτώσουμε μια ήδη υπάρχουσα, από το υπομενού <Open New Rename List>. 
Από το <New Rename List> επιλέγουμε το directory που περιέχει τα άλμπουμ που θέλουμε να μορφοποιήσουμε.
Το πρόγραμμα ψάχνει σε όλα τα subdirectory του directory που άνοιξες και βρίσκει τους φακέλους που περιέχουν αρχεία FLAC, mp3, m4a, ogg κλπθεωρώντας τους φακέλους που περιέχουν άλμπουμ. 
Η δημιουργία της λίστας μπορεί να είναι αυτόματη ή χειροκίνητη, η επιλογή γίνεται από το σχετικό παράθυρο που εμφανίζεται. 
Αν επιλέξεις <New Rename List>, το πρόγραμμα δημιουργεί ένα φύλλο Excel (και ένα παρόμοιο αρχείο κειμένου CSV) με τα ονόματα, πως είναι τώρα και πως προτείνει να γίνουν. 
Αν οι προτάσεις του προγράμματος δεν σε ικανοποιούν, μπορείς να επέμβεις στο Excel και να κάνεις όποιες αλλαγές θέλεις και στη συνέχεια να το φορτώσεις στο πρόγραμμα και να προχωρήσεις στην μετονομασία. 
Αν προτιμάς, μπορείς να κάνεις τις αλλαγές κατευθείαν στον ενσωματωμένο στο πρόγραμμα editor, ο οποίος φορτώνει αυτόματα την λίστα από το CSV, μόλις αυτή δημιουργηθεί.  
ΠΡΟΣΟΧΗ: Οι αλλαγές που γίνονται στον ενσωματωμένο Editor δεν σώζονται και στο Excel, αλλά μόνο στο CSV. Και φυσικά, οι αλλαγές που κάνεις στο Excel δεν σώζονται στο CSV, αλλά μόνο στο Excel. Οπότε ή θα δουλέψεις τις αλλαγές σου στο Excel, (και στη συνέχεια θα το φορτώσεις στο πρόγραμμα), ή στον editor του προγράμματος. 
Τελικά, από το υπομενού <Rename Now> πραγματοποιείς την μετονομασία, (σύμφωνα με την λίστα που είναι φορτωμένη στον Editor). 
Εναλλακτικά, από το υπομενού <Rename from List>, η μετονομασία γίνεται κατ' ευθείαν από μια υπάρχουσα λίστα, (Excel ή CSV)χωρίς την δυνατότητα περαιτέρω επεξεργασίας στον Editor. (Η όποια τυχούσα επεξεργασία θα πρέπει να έχει γίνει πριν φορτωθεί η λίστα) 
Αν μετανιώσεις, υπάρχει το υπομενού <Undo Last Rename>. Αν θες να επαναφέρεις παλιότερη μετονομασία που έκανες, απλά εναλλάσσεις αμοιβαία τις στήλες Old_Name και New_Name στο αρχείο Rename_List που έχει δημιουργηθεί στον root φάκελο που έκανες τις αλλαγές και φορτώνεις την λίστα από το <Rename from List>.

Ο μηχανισμός μορφοποίησης είναι ο εξής:
Αρχικά, το πρόγραμμα σκανάρει τα ονόματα των άλμπουμ για να βρει ημερομηνίες. Αν βρει μία, θεωρεί ότι αυτή είναι η ημερομηνία κυκλοφορίας του, (είναι συνήθης πρακτική να γράφουν οι τορεντάδες στο όνομα του φακέλου ενός άλμπουμ και την ημερομηνία κυκλοφορίας του). Αν βρει παραπάνω από μία ημερομηνία (συνήθως η δεύτερη είναι αυτή του remaster) σε ρωτάει πια θες, προτείνοντας την παλαιότερη. (Στην αυτόματη λειτουργία δεν ρωτάει, αλλά επιλέγει μόνο του την πιο παλιά ημερομηνία). Αν δεν βρει ημερομηνία στο όνομα του φακέλου, ψάχνει για ημερομηνία στα metadata των τραγουδιών του άλμπουμ. Αν δεν βρει κι εκεί, καλεί την βάση δεδομένων του Spotify και αντλεί τις πληροφορίες από εκεί. Έτσι, φτιάχνει, όχι μόνο την ημερομηνία κυκλοφορίας, αλλά και όλα τα metadata που λείπουν από το άλμπουμ. 
Επί πλέον, καθαρίζει τα ονόματα των φακέλων από τα σκουπίδια των τορεντάδων, (spaces, underscores κλπ.). 

Το πρόγραμμα διαθέτει μια λίστα με λέξεις που πρέπει να διαγράψει ή να αλλάξει, αλλά μπορεί και ο χρήσης να προσθέσει ή να αφαιρέσει λέξεις, από το υπομενού <Words to Rename> του μενού <Rename>.
Στη λίστα που εμφανίζεται, προσθέτεις λέξεις που θες να αλλάξουν, ενώ με δεξί κλικ αφαιρείς ή αλλάζεις λέξεις. Στο πεδίο <Change> εισάγεις τη λέξη που θέλεις να αλλάζει και στο πεδίο <To> τη λέξη που θα την αντικαθιστά και στη συνέχεια πατάςτο <Submit> για να προστεθεί η λέξη στη λίστα. Όταν ολοκληρώσεις την εισαγωγή λέξεων προς αλλαγή ή διαγραφή από τα ονόματα των άλμπουμ, πατάς το <Close> για να σωθούν και να κλείσει το παράθυρο. Αν θες μια λέξη να διαγράφεται από τα ονόματα των άλμπουμ, απλά αφήνεις κενό το πεδίο <To>.

Άλλα Εργαλεία:
Από το υπομενού <Move to ABC>, του μενού <Tools>, το πρόγραμμα ομαδοποιεί όλα τα άλμπουμ σε φακέλους αλφαβητικά (A, B, C, D, E, ....Z), βάσει του πρώτου γράμματος του ονόματος του καλλιτέχνη, στη συνέχεια ανά καλλιτέχνη και τέλος ανά άλμπουμ. Η διαδικασία για να γίνει αυτό έχει ως εξής: Αρχικά σκανάρει τον root φάκελο που επιλέγεις, βρίσκει τους φακέλους των άλμπουμ και φτιάχνει έναν φάκελο για κάθε καλλιτέχνη, στον οποίο μεταφέρει όλα του τα άλμπουμ, στη συνέχεια συγκεντρώνει όλους τους φακέλους καλλιτεχνών με το ίδιο πρώτο γράμμα στο όνομα τους στους φακέλους που δημιουργεί από αυτό το πρώτο γράμμα (A, B, C...). 
Εάν έχεις άλμπουμ MQA, με το <MQA Tag Restorer> ,(πάντα στο μενού <Tools>), φτιάχνεις τα Tag, το όνομα και την δομή αρχείων και φακέλων, ώστε αυτά να μπορούν να τα παίζουν και στα consumer player , ενώ από το <Fix MQA>, του μενού <Tools>, το πρόγραμμα διαγράφει τα σκουπίδια και τα διπλά αρχεία που δημιουργεί το <MQA Tag Restorer>.

"""
        self.__fr = Frame(self.top3, borderwidth=2)
        self.__fr.pack(expand=True, fill='both')
        self.__help_text = Text(self.__fr)
        self.__help_text.pack(side=LEFT, expand=True, fill='both')
        self.__help_text.insert(1.0, info_text)
        self.__help_text.configure(state='disabled', fg='black', bg='lightyellow', border=0, relief="groove",
                                   wrap='word', padx=12)
        self.__helpScrollBar = Scrollbar(self.__fr, cursor='arrow')
        self.__helpScrollBar.config(command=self.__help_text.yview)
        self.__help_text.config(yscrollcommand=self.__helpScrollBar.set)
        self.__helpScrollBar.pack(side=RIGHT, fill=Y)

    def __show_about(self):
        self.top2 = tk.Toplevel()
        self.top2.geometry('+%d+%d' % (self.left * 2 - 233, self.top * 2 - 370))
        self.top2.title("About...")
        self.top2.grab_set()
        try:
            self.about_image = tk.PhotoImage(file=os.path.join('images', 'angel.gif'))
            self.about_label = tk.Label(self.top2, image=self.about_image)
            self.about_label.image = self.about_image
            self.about_label.pack(expand=True, fill='both')
        except TclError as error:
            self.__write_error_log(error)
        finally:
            pass
        self.about_label2 = tk.Label(self.top2, text='FixEm Beta' + '\n' + 'EcoG is GreaT')
        self.about_label2.pack(expand=True, fill='both')

    def __new_rename_list(self):
        if self.__rootTextArea.edit_modified():
            self.__MsgBox = tk.messagebox.askquestion('Save List?', 'Rename List has changed. Do You Want to Save It?',
                                                      icon='warning')
            if self.__MsgBox == 'yes':
                self.__save_rename_list()
        self.__root.title("Create a New Rename List")
        self.__file = None
        self.__my_choice = "make_list"
        self.list_type = None
        self.top1 = Toplevel(self.__root)
        self.top1.geometry('+%d+%d' % (self.left, self.top))
        self.top1.title('Question:')
        self.w = tk.Label(self.top1, text='Ηow do you want the list to be created?')
        self.w.pack(fill='both', expand=1)
        self.v = tk.StringVar(None, 'quick')
        if darkdetect.isDark():
            tk.Radiobutton(self.top1, text='Auto', variable=self.v, value='quick', selectcolor='black',
                           padx=5, pady=5).pack(anchor='w')
            tk.Radiobutton(self.top1, text='Manual', variable=self.v, value='slow', selectcolor='black',
                           padx=5, pady=5).pack(anchor='w')
        else:
            tk.Radiobutton(self.top1, text='Auto', variable=self.v, value='quick',
                           padx=5, pady=5).pack(anchor='w')
            tk.Radiobutton(self.top1, text='Manual', variable=self.v, value='slow',
                           padx=5, pady=5).pack(anchor='w')
        self.b = tk.Button(self.top1, text="OK", font="Arial 12", command=self.button_pushed)
        self.b.pack(fill='none', expand=0)
        self.top1.focus()
        self.top1.update()

    def button_pushed(self):
        self.list_type = self.v.get()
        self.top1.destroy()
        self.top1.update()  # Kill the root window!
        self.__new_list()

    def __new_list(self):
        self.__rootPath = askdirectory(title='Choose your albums Folder', mustexist=True)  # Returns opened path as str
        if self.wizard_on:
            self.wiz_top.focus()
        if self.__rootPath == "":
            self.__rootPath = None
            self.__root.title("Fix'em")
        else:
            self.status_str = "Working..."
            if self.wizard_on:
                self.wiz_top.iconify()
            self.__pb = ttk.Progressbar(self.top_f, orient=HORIZONTAL, length=200, mode="indeterminate", takefocus=True,
                                        maximum=100)
            self.__pb.pack(side='left', expand=False, fill='x', padx=8)
            self.bar_thread = threading.Thread(target=self.__pb.start())
            self.term.pack(side='right', expand=0, fill='x')
            self.term_label.pack(side='right', expand=0, fill='x')
            self.__root.title("Please Wait...")
            lista = self.__find_album(self.__rootPath)
            self.__pb.update()
            if len(lista) != 0:
                albums_string = ' Albums'
                if len(lista) == 1:
                    albums_string = ' Album'
                self.status_str =  'We found ' + str(
                        len(lista)) + albums_string + '. Now We Are Preparing the Rename List, It might Take Some Time... '
                self.__rootScrollBar.pack(side=RIGHT, fill=Y)
                self.__rootScrollBar2.pack(side=BOTTOM, fill=X)
                self.__rootTextArea.pack(expand=True, fill='both')

                self.__rootTextArea.delete(1.0, END)
                self.__rootTextArea.tag_add('highlightline', '1.0', '1.' + str(len(str(len(lista))) + 15))
                self.__rootTextArea.tag_configure('highlightline', background='yellow', font='TkFixedFont',
                                                  relief='raised')
                self.__rootTextArea.insert(1.0, 'We found ' + str(
                    len(lista)) + albums_string + ' . Now We Are Preparing the Rename List, It might Take Some Time... ',
                                           'highlightline')
                self.__make_list(lista)
                self.status_str ="Done!"
                self.__pb.stop()
                self.__pb.destroy()
                self.__pb.update()
                if self.__my_choice == "do_rename":
                    done_msg = "Rename Finished"
                else:
                    done_msg = "Rename List is Ready"
                showinfo(title='Done!', message=done_msg)
            else:
                self.status_str = "You Can Always Try Again :-)"
                self.__pb.stop()
                self.__pb.destroy()
                self.__pb.update()
                showinfo(title='Eeeeeeeep!', message="There Are No Albums Here")

    def __find_album(self, _path):
        # path_dict = {'_root': '_root', 'subdirectory': 'subdirectory'}
        lista = list()
        extension = ''
        for _root, subdirectories, files in os.walk(_path):
            _root = _root.replace('/', '\\')
            for subdirectory in subdirectories:
                for file in os.listdir(os.path.join(_root, subdirectory)):
                    extension = file.split('.')[-1].casefold()
                    if extension == "flac" or extension == "m4a" or extension == "mp3" or extension == "ogg" or extension == "mp4":
                        break
                if extension == "flac" or extension == "m4a" or extension == "mp3" or extension == "ogg" or extension == "mp4":
                    if subdirectory == 'MQA' or subdirectory[:2] == 'CD':
                        if subdirectory == 'MQA' and (_root.split("\\")[-1])[:2] == 'CD':
                            path_dict = {'_root': _root.rsplit("\\", 2)[0], 'subdirectory': _root.split('\\')[-2]}
                        else:
                            path_dict = {'_root': _root.rsplit("\\", 1)[0], 'subdirectory': _root.split('\\')[-1]}
                        if len(lista) == 0:
                            lista.append(path_dict)
                        elif path_dict != lista[len(lista) - 1]:
                            lista.append(path_dict)
                    else:
                        path_dict = {'_root': _root, 'subdirectory': subdirectory}
                        lista.append(path_dict)
        return lista

    def __make_list(self, lista):
        self.__final_lista = [{}]
        for r in lista:
            self.__album_rename(r)
        if self.__final_lista == [{}]:
            return  # TODO
        else:
            try:
                workbook = xlsxwriter.Workbook(os.path.join(self.__rootPath, 'Rename_List.xlsx'))
                worksheet = workbook.add_worksheet()
                worksheet.write(0, 0, 'Path')
                worksheet.write(0, 1, 'Old_Name')
                worksheet.write(0, 2, 'New_Name')
                row = 0
                for final_dict in self.__final_lista:
                    path = final_dict.get('Path')
                    old_name = final_dict.get('Old_Name')
                    new_name = final_dict.get('New_Name')
                    worksheet.write(row, 0, path)
                    worksheet.write(row, 1, old_name)
                    worksheet.write(row, 2, new_name)
                    row += 1
                workbook.close()
                with open(os.path.join(self.__rootPath, 'Rename_List.csv'), 'w', encoding="utf-8",
                          newline='') as csvfile:
                    fieldnames = ['Path', 'Old_Name', 'New_Name']
                    writer = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldnames)
                    writer.writeheader()
                    for f in self.__final_lista:
                        if f:
                            writer.writerow(f)
            except OSError as error:
                self.__write_error_log(error)
            finally:
                pass
            self.__root.title('Rename List:')  # set the window title
            self.write_list_tex()

    def __album_rename(self, r):
        self.__pb.update()
        _path = os.path.join(r['_root'], r['subdirectory'])
        n = r['subdirectory']
        if os.path.isdir(_path):
            _old_name = n
            dates = []
            date = ''
            new_date = ""
            for date in re.findall('\\d+-\\d+', n):
                n = n.replace(date, '')  # remove year ranges
            for date in re.findall('\\d+ - \\d+', n):
                n = n.replace(date, '')
            for date in re.findall('\\d+', n):  # Find possible dates in Album name / description
                if len(date) == 4:  # Add only 4 digit years
                    if date.startswith("19") or date.startswith("20"):
                        dates.append(date)  # Add only years from 1900 to 2100
            n = self.fix_m_e(_old_name)
            if not dates:
                dates = self.__get_date_from_tag(_path)
                # if no dates are found get them from the album's songs or Spotify
                if self.list_type == 'slow':
                    if dates is None:  # If no Dates returned from the album's songs and Spotify
                        self.__root.withdraw()
                        while True:
                            new_date = str(askinteger(title="No years have been found",
                                                      prompt="Please enter a Valid Year for:" + "\n" + "'" + n + "'",
                                                      minvalue=1890, maxvalue=2100))
                            self.__root.deiconify()
                            if new_date == "" or new_date is None or len(new_date) != 4:
                                continue
                            else:
                                break
                if not dates:
                    dates = [new_date]
            if (len(dates)) == 1:
                new_date = dates[0]  # Reset date
            if dates != [] and dates is not None:
                dates = list(dict.fromkeys(dates))  # remove duplicates
                dates.sort()
                if self.list_type == 'quick' or (len(dates)) == 1:
                    new_date = dates[0]
                else:
                    all_dates = ""
                    for a in dates:
                        all_dates = all_dates + ", " + a
                    all_dates = all_dates.lstrip(", ")
                    while True:
                        self.__root.withdraw()
                        new_date = str(askinteger(title="Multiple years have been found!",
                                                  prompt="In: '" + n + "'" + "\n" + "multiple years have been found:" + "\n"
                                                         + all_dates + "\n" + "Please Enter the Right Year:",
                                                  initialvalue=int(dates[0]), minvalue=1890, maxvalue=2100))
                        self.__root.deiconify()
                        if new_date == "" or new_date is None:
                            new_date = dates[0]
                        elif len(new_date) != 4 or not new_date.isdigit():
                            continue
                        else:
                            break
            if len(new_date) > 0:
                n = n.replace(new_date, '', 1)  # remove date, if exists
            n = self.__beautify(n)
            if len(new_date) > 0:
                n = new_date + ". " + n  # put date at the begging
            final_dict = {'Path': r['_root'], 'Old_Name': _old_name, 'New_Name': n}
            self.__final_lista.append(final_dict)
            if self.__my_choice == "do_rename":
                try:
                    os.rename(os.path.join(r['_root'], _old_name), os.path.join(r['_root'], n))  # Rename
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    pass

    def __get_date_from_tag(self, album_dir):
        album = None
        artist = None
        dates = None
        for _root, subdirectories, files in os.walk(album_dir):
            _root = _root.replace('/', '\\')
            # for subdirectory in subdirectories:
            dates = list()
            album = None
            artist = None
            for s in files:
                if os.path.isfile(os.path.join(_root, s)):
                    extension = (s.split(".")[-1]).casefold()
                    if extension == "flac" or extension == "m4a" or extension == "mp3" or extension == "ogg":
                        try:
                            song = taglib.File(os.path.join(_root, s))
                            if 'DATE' in song.tags:
                                date = max(song.tags['DATE'])
                                for d in re.findall('^([1][9]\d\d|2[0-9][0-9][0-9])$', date):
                                    dates.append(d)
                            if artist is None:
                                if 'ALBUMARTIST' in song.tags:
                                    artist = song.tags['ALBUMARTIST'][0]
                                elif 'ARTIST' in song.tags:
                                    artist = song.tags['ARTIST'][0]
                            if album is None:
                                if 'ALBUM' in song.tags:
                                    album = song.tags['ALBUM'][0]
                        except OSError as error:
                            self.__write_error_log(error)
                        finally:
                            pass
        if album is None:
            album_dir_split = album_dir.split('\\')
            if len(album_dir_split) > 1:
                artist = album_dir_split[-2]
            if len(album_dir_split) > 0:
                album = album_dir_split[-1]
            album = album.replace(artist + ' - ', '', 1)
        if artist is not None and album is not None:
            dates = self.__ask_spotify(artist, album)
        if dates is not None:
            dates = list(dict.fromkeys(dates))  # remove duplicates
        return dates

    @staticmethod
    def __ask_spotify(artist, album):
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        load_dotenv()
        cid = os.getenv("cid")
        secret = os.getenv("secret")
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        dates = list()
        results = sp.search(q="artist:" + artist + " album:" + album, type="album")
        items = results["albums"]["items"]
        if len(items) == 0:
            return None
        else:
            i = 0
            while i < len(items):
                d = items[i]
                dates.append(d["release_date"])
                i = i + 1
        i = 0
        while i < len(dates):
            dates[i] = (dates[i].split("-"))[0]
            i = i + 1
        dates = list(dict.fromkeys(dates))
        return dates

    def __rename(self):
        self.__root.title("Rename Albums Directly")
        self.__file = None
        self.__my_choice = "do_rename"
        self.__rootPath = askdirectory(mustexist=True)  # Returns opened path as str
        if self.__rootPath == "":
            self.__rootPath = None
        else:
            self.__rootTextArea.configure(cursor="watch")
            self.status_str = "Working..."
            self.__rootTextArea.delete(1.0, END)
            self.__new_list()

    def __open_rename_list(self):
        if self.__rootTextArea.edit_modified():
            self.__MsgBox = tk.messagebox.askquestion('Save List?', 'Rename List has changed. Do You Want to Save It?',
                                                      icon='warning')
            if self.__MsgBox == 'yes':
                self.__save_rename_list()
                self.__rootTextArea.edit_modified(False)
        self.__file = askopenfilename(title='Open a Rename List', initialfile='Rename_List.csv',
                                      defaultextension=".csv",
                                      filetypes=[("CSV", "*.csv"), ("Excel", "*.xl*")])
        if self.__file == "":  # no file to open
            self.__file = None
        else:
            self.__rootPath = self.__file.rsplit('/', maxsplit=1)[0]
            extension = self.__file.split(".")[-1]
            if extension == 'csv':
                df = pd.read_csv(self.__file)
            elif extension == 'xls' or extension == 'xlsx':
                df = pd.read_excel(self.__file)
            else:
                self.__rename_from_list()
            if list(df.columns) != ['Path', 'Old_Name', 'New_Name'] and list(df.columns) != ['Path|Old_Name|New_Name']:
                showerror(title='Error!', message='Please Open a VALID Rename File')
                return
            self.status_str = "OK"
            self.term.pack(side='right', expand=0, fill='x')
            self.term_label.pack(side='right', expand=0, fill='x')
            self.__root.title(os.path.basename(self.__file))  # set the window title
            self.__rootScrollBar.pack(side=RIGHT, fill=Y)
            self.__rootScrollBar2.pack(side=BOTTOM, fill=X)
            self.__rootTextArea.pack(expand=True, fill='both')
            # self.__rootTextArea.delete(1.0, END)
            self.__final_lista = [{}]
            i = 0
            while i in df.index:
                try:
                    _path = df.loc[i][0]
                    _old_name = df.loc[i][1]
                    _new_name = df.loc[i][2]
                    i += 1
                except IndexError as error:
                    _old_name = ''
                    _new_name = ''
                    self.__write_error_log(error)
                    i += 1
                except OSError as error:
                    self.__write_error_log(error)
                    i += 1
                finally:
                    pass
                final_dict = {'Path': _path, 'Old_Name': _old_name, 'New_Name': _new_name}
                self.__final_lista.append(final_dict)
            self.write_list_tex()

    def write_list_tex(self):
        self.__rootTextArea.delete(1.0, END)
        paths = []
        olds = []
        for d in self.__final_lista:
            if d:
                final_path = len(d['Path'])
                paths.append(final_path)
                final_old = len(d['Old_Name'])
                olds.append(final_old)
        if paths:
            max_path = max(paths)
        else:
            max_path = 0
        if olds:
            max_old_name = max(olds)
        else:
            max_old_name = 0
        path_spaces = max_path - len('Path') + 2
        old_spaces = max_old_name - len('Old_Name') + 2
        self.__rootTextArea.tag_configure('blue_white', background='blue', foreground='white', relief='raised')
        self.__rootTextArea.insert(1.0, 'Path' + path_spaces * ' ' + 'Old_Name' + old_spaces * ' ' + 'New_Name' +
                                   '\n', 'blue_white')
        if self.__final_lista is None:
            showinfo(title='Warning!', message="Th Rename List is Empty")
        else:
            self.__rootTextArea.tag_configure('light_yellow', background='lightyellow', relief='sunken',
                                              selectbackground='blue')
            self.__rootTextArea.tag_configure('light_blue', background='lightblue', relief='raised',
                                              selectbackground='blue')
            i = 1
            for final_dict in self.__final_lista:
                if final_dict != {}:
                    if i % 2:
                        tag = 'light_yellow'
                    else:
                        tag = 'light_blue'
                    self.__rootTextArea.insert('end', '{0}{1}{2}\n'.format(final_dict['Path'].ljust(max_path + 2),
                                                                           final_dict[
                                                                               'Old_Name'].ljust(max_old_name + 2),
                                                                           final_dict['New_Name']), tag)
                    i += 1
        self.__rootTextArea.edit_modified(False)

    def __rename_now(self):
        if self.__rootTextArea.compare("end-1c", "==", "1.0"):
            showinfo(title='Eeeeep!', message='There IS Nothing to Rename!')
            return
        if self.__rootTextArea.edit_modified():
            self.__MsgBox = tk.messagebox.askquestion('Save List?', 'Rename List has changed. Do You Want to Save It?',
                                                      icon='warning')
            if self.__MsgBox == 'yes':
                self.__save_rename_list()
                self.__rootTextArea.edit_modified(False)
        lines = (self.__rootTextArea.get('1.0', 'end')).split('\n')
        for line in lines:
            if line == lines[0]:
                continue
            cells = line.split('  ')
            save_cells = list()
            for cell in cells:
                save_cell = cell.strip()
                if save_cell != '':
                    save_cells.append(save_cell)
            if len(save_cells) == 3:
                final_dict = {'Path': save_cells[0], 'Old_Name': save_cells[1], 'New_Name': save_cells[2]}
                if final_dict != {}:
                    self.__final_lista.append(final_dict)
                    try:
                        os.rename(os.path.join(final_dict['Path'], final_dict['Old_Name']),
                                  os.path.join(final_dict['Path'], final_dict['New_Name']))
                    except OSError as error:
                        self.__write_error_log(error)
                    finally:
                        pass
        self.__rootTextArea.edit_modified(False)
        self.status_str = "Rename Finished!"
        self.__root.title("Fix'em All")
        err_log = os.path.join(self.__rootPath, "errorlog.txt")
        if os.path.exists(err_log):
            if not self.wizard_on:
                showinfo(title='Done!', message='Rename Finished with Errors/n Press OK to See the Error Log')
            try:  # TODO
                # if root.tk.call('tk', 'windowingsystem') == 'win32':
                os.startfile(err_log)
            # else:
            # webbrowser.open(err_log)
            except OSError as error:
                self.__write_error_log(error)
            finally:
                pass
        else:
            if not self.wizard_on:
                showinfo(title='Done!', message='Rename Finished')

    def __rename_from_list(self):
        global df, path, old_name, new_name
        if self.__rootTextArea.edit_modified():
            self.__MsgBox = tk.messagebox.askquestion('Save List?', 'Rename List has changed. Do You Want to Save It?',
                                                      icon='warning')
            if self.__MsgBox == 'yes':
                self.__save_rename_list()
        self.__file = askopenfilename(initialfile='Rename_List.xlsx', defaultextension=".xlsx",
                                      filetypes=[("Excel", "*.xl*"), ("CSV", "*.csv")])
        if self.__file == "":  # no file to open
            self.__file = None
        else:
            self.__rootPath = self.__file.rsplit('/', maxsplit=1)[0]
            extension = self.__file.split(".")[-1]
            if extension == 'csv':
                df = pd.read_csv(self.__file)
            elif extension == 'xls' or extension == 'xlsx':
                df = pd.read_excel(self.__file)
            else:
                self.__rename_from_list()
            if list(df.columns) != ['Path', 'Old_Name', 'New_Name'] and list(df.columns) != ['Path|Old_Name|New_Name']:
                showerror(title='Error!', message='Please Open a VALID Rename File')
                return
            self.__root.title("Rename From List")
            self.status_str = "Working..."
            self.__root.title(os.path.basename('Renaming from ' + self.__file))  # set the window title
            self.__rootScrollBar.pack(side=RIGHT, fill=Y)
            self.__rootScrollBar2.pack(side=BOTTOM, fill=X)
            self.__rootTextArea.pack(expand=True, fill='both')
            self.__rootTextArea.delete(1.0, END)
            self.__final_lista = [{}]
            i = 0
            while i in df.index:
                try:
                    path = df.loc[i][0]
                    old_name = df.loc[i][1]
                    new_name = df.loc[i][2]
                    i += 1
                except IndexError as error:
                    old_name = ''
                    new_name = ''
                    self.__write_error_log(error)
                    i += 1
                except OSError as error:
                    self.__write_error_log(error)
                    i += 1
                finally:
                    pass
                final_dict = {'Path': path, 'Old_Name': old_name, 'New_Name': new_name}
                self.__final_lista.append(final_dict)
            if self.__final_lista is None:
                showinfo(title='Warning!', message="Rename List is Empty")
            else:
                self.write_list_tex()

                for final_dict in self.__final_lista:  # Rename
                    try:
                        if final_dict != {}:
                            os.rename(os.path.join(final_dict['Path'], final_dict['Old_Name']),
                                      os.path.join(final_dict['Path'], final_dict['New_Name']))

                    except OSError as error:
                        self.__write_error_log(error)
                    finally:
                        pass
            # self.__rootTextArea.edit_modified(False)
            self.status_str= "Done!"
            showinfo(title='Done!', message='Rename from List Finished')

    def __undo(self):
        if self.__final_lista is None:
            showinfo(title='Warning!', message="There Is Nothing to Undo")
        else:
            for final_dict in self.__final_lista:
                try:  # Undo Rename
                    if final_dict != {}:
                        os.rename(os.path.join(final_dict['Path'], final_dict['New_Name']),
                                  os.path.join(final_dict['Path'], final_dict['Old_Name']))
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    pass
            showinfo(title='Done!', message="Undo Finished")

    def create_artist_files(self):
        _path = askdirectory()  # Returns opened path as str
        if _path == "" or _path is None:
            return  # Exit programm if user CANCELs the file open dialog
        self.list_type = 'slow'
        # self.__rootPath = _path
        lista = os.listdir(_path)
        self.status_str = "Working..."
        for n in lista:
            artist = None
            artist_folder = None
            folder_name = os.path.join(_path, n)
            if os.path.isfile(folder_name):
                continue
            if n.find('-') == -1:
                artist = self.get_artist_from_tag(folder_name)
            else:
                artist = (n.rsplit('-', maxsplit=1)[0]).rstrip()
            if artist is None:
                continue
            artist_folder = os.path.join(_path, artist)
            if not os.path.exists(artist_folder):
                try:
                    os.makedirs(artist_folder)
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    pass
            if os.path.exists(artist_folder):
                try:
                    shutil.move(folder_name, artist_folder, copy_function=shutil.copytree)
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    continue
        self.status_str = "Done!"
        if tk.messagebox.askquestion('Finished!', 'Artist Folders Created.\nDo You Want to Move them to ABC?',
                                     icon='question') == 'yes':
            self._abc(_path)

    def get_artist_from_tag(self, _path):
        artist = None
        artists = list()
        songs = os.listdir(_path)
        for s in songs:
            if os.path.isfile(os.path.join(_path, s)):
                extension = (s.split(".")[-1]).casefold()
                if extension == "flac" or extension == "m4a" or extension == "mp3" or extension == "ogg":
                    try:
                        song = taglib.File(os.path.join(_path, s))
                    except OSError as error:
                        self.__write_error_log(error)
                    finally:
                        pass
                    if 'ALBUMARTIST' in song.tags:
                        artist = song.tags['ALBUMARTIST'][0]
                        return artist
                    elif 'ARTIST' in song.tags:
                        artists.append(song.tags['ARTIST'][0])
        artists = list(dict.fromkeys(artists))
        if len(artists) == 0:
            artist = None
        elif len(artists) == 1:
            artist = artists[0]
        else:
            artist = 'Various Artists'
        return artist

    def __abc_open_folder(self):
        _path = askdirectory()  # Returns opened path as str
        if _path != "":
            self._abc(_path)

    def _abc(self, _path):
        self.list_type = 'slow'
        # self.__rootPath = _path
        lista = os.listdir(_path)
        self.status_str = "Working..."
        for n in lista:
            if os.path.isfile(os.path.join(_path, n)):
                continue
            if n[0].isalpha():
                _abc = n[0].capitalize()
            else:
                _abc = "0"
            if not os.path.exists(os.path.join(_path, _abc)):
                try:
                    os.mkdir(os.path.join(_path, _abc))
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    pass
            if os.path.isfile(os.path.join(_path, n)):
                continue
            if os.path.isdir(os.path.join(_path, _abc, n)):  # if folder already exists
                list_dir = os.listdir(os.path.join(_path, n))
                content_list = []
                for val in list_dir:
                    path_dir = os.path.join(_path, n, val)
                    content_list.append(path_dir)
                merge_folder = _abc
                merge_folder_path = os.path.join(_path, merge_folder, n)
                for sub_dir in content_list:
                    dir_to_move = os.path.join(_path, n, sub_dir)
                    shutil.move(dir_to_move, merge_folder_path, copy_function=shutil.copytree)
                if len(os.listdir(os.path.join(_path, n))) == 0:
                    try:
                        os.rmdir(os.path.join(_path, n))
                    except OSError as error:
                        self.__write_error_log(error)
                    finally:
                        pass
            else:
                try:
                    shutil.move(os.path.join(_path, n), os.path.join(_path, _abc), copy_function=shutil.copytree)
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    pass
        showinfo(title='Status', message='All Done!')

    def __save_rename_list(self):
        if len(self.__rootTextArea.get("1.0", "end-1c")) == 0:
            showinfo(title='Eeeeeep!', message='Please Make a List First')
            return
        if self.__rootTextArea.edit_modified():
            self.__file = asksaveasfilename(initialfile='Rename_List.csv',
                                            defaultextension=".csv",
                                            filetypes=[("Comma Separated Documents", ".csv"), ("All Files", "*.*")])
            if self.__file == "":
                self.__file = None
                return
            # Try to save the file
            lines = (self.__rootTextArea.get('1.0', 'end')).split('\n')
            try:
                with open(self.__file, 'w', encoding="utf-8", newline='') as csvfile:
                    fieldnames = ['Path', 'Old_Name', 'New_Name']
                    file = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldnames)
                    for line in lines:  # data frames to csv
                        cells = line.split('  ')
                        save_cells = list()
                        for cell in cells:
                            save_cell = cell.strip()
                            if save_cell != '':
                                save_cells.append(save_cell)
                        if len(save_cells) == 3:
                            final_dict = {'Path': save_cells[0], 'Old_Name': save_cells[1], 'New_Name': save_cells[2]}
                            file.writerow(final_dict)
            except OSError as error:
                self.__write_error_log(error)
            finally:
                pass
            self.__rootTextArea.edit_modified(False)
            self.status_str = "Rename File Saved"
            self.__root.title(os.path.basename(self.__file) + " - Fix'em All")

    def __cut(self):
        self.__rootTextArea.event_generate("<<Cut>>")

    def __copy(self):
        self.__rootTextArea.event_generate("<<Copy>>")

    def __paste(self):
        self.__rootTextArea.event_generate("<<Paste>>")

    def __edit_undo(self):
        try:
            self.__rootTextArea.edit_undo()
        except TclError as error:
            showerror(title='Eeeep!', message=str(error))
        finally:
            pass

    def __edit_redo(self):
        try:
            self.__rootTextArea.edit_redo()
        except TclError as error:
            showerror(title='Eeeep!', message=str(error))
        finally:
            pass

    def search(self, event):
        indx = '1.0'
        term = self.term.get()
        self.__rootTextArea.tag_remove('found', '1.0', 'end')
        if term == '':
            return
        while True:
            indx = self.__rootTextArea.search(term, indx, nocase=True,
                                              stopindex='end')
            if not indx: break
            endindx = '{}+{}c'.format(indx, len(term))
            self.__rootTextArea.tag_add('found', indx, endindx)
            indx = endindx

    def remove_duplicate_audio(self):
        """
        Removes duplicate audio files within a directory.

        Args:
            directory: The path to the directory containing audio files.
        """

        self.__root.title("Find Duplicates")
        audio_files = {}  # Dictionary to store file hashes and paths
        duplicates_removed = 0
        filepath = ""
        directory = askdirectory(
            title='Choose Folder to Scan for Duplicates', mustexist=True)
        if directory == "":
            directory = None
            self.__root.title("Fix'em")
            return

        for foldername, subfolders, filenames in os.walk(directory):
            self.status_str = f"Processing Folder: {foldername}"
            self.status_label.config(text=self.status_str)
            self.status_label.update_idletasks()
            for subfolder in subfolders:
                self.status_str = f"Processing Subfolder: {os.path.join(foldername, subfolder)}"
                self.status_label.config(text=self.status_str)
                self.status_label.update_idletasks()
            for file_name in filenames:
                filename  = os.path.join(foldername, file_name)
                if filename.lower().endswith(('.mp3', '.wav', '.flac', '.aac',
                                              '.m4a')):  # Add more extensions as needed
                    filepath = os.path.join(directory, filename)
                    self.status_str = 'Processing: '+ filename
                    self.status_label.config(text=self.status_str)
                    self.status_label.update_idletasks()

                    try:
                        file_hash = self.calculate_file_hash(filepath)

                        if file_hash in audio_files:
                            # Duplicate found!  Keep the first one encountered (you can modify this)
                            original_filepath = audio_files[file_hash]
                            file_size_original = os.path.getsize(original_filepath)
                            file_size_duplicate = os.path.getsize(filepath)

                            # Compare file sizes (optional, but good practice)
                            if file_size_original == file_size_duplicate:
                                print(
                                    f"Duplicate found: {filename} (same size as {os.path.basename(original_filepath)})")
                                os.remove(filepath)
                                duplicates_removed += 1
                            else:
                                print(
                                    f"Potential duplicate found: {filename} (different size than {os.path.basename(original_filepath)})")
                                print(
                                    f"Keeping: {os.path.basename(original_filepath)} and {filename}")  # Decide which to keep manually.
                                # os.remove(filepath) #uncomment if you want to remove the different size duplicate
                                # duplicates_removed += 1

                        else:
                            audio_files[file_hash] = filepath  # Add file hash and path to the dictionary
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")

        self.status_str = f"Finished. {duplicates_removed} duplicate files removed."
        self.status_label.config(text=self.status_str)
        self.status_label.update_idletasks()

    def calculate_file_hash(self, filepath):
        """Calculates the SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as file:  # Open in binary mode
            while True:
                chunk = file.read(4096)  # Read in chunks for large files
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def loudness(self):
        self.__root.title("Measure Loudness")
        audio_file = askopenfilename(
            title='Choose an audio file', filetypes=(('FLAC', '*.flac'), ('MP3', '*.mp3'),
                                                     ('WAV', '*.wav'), ('OGG', '*.ogg'), ('AIFF (Apple/SGI)', '*.aiff'),
                                                     ('RAW (header-less)', '*.raw')))
        print(audio_file)
        if audio_file == "":
            self.__root.title("Fix'em")
            return
        # Load an audio file
        audio, sr = librosa.load(audio_file)

        # Calculate the loudness
        rms = librosa.feature.rms(y=audio)
        loudness = librosa.core.amplitude_to_db(rms, ref=1.0, top_db=80.0)

        self.status_str = f"{audio_file} loudness (dB): {loudness[0][0]:2f}"
        self.status_label.config(text=self.status_str)
        self.status_label.update_idletasks()

        print("Loudness (dB):", loudness[0][0])

    @staticmethod
    def fix_m_e(name):
        name = name.replace('[E]', '')  # Remove [E], if any
        name = name.replace('[AE]', '[A]')
        name = name.replace('[ME]', '[M]')
        mqa = name.find("[M]")
        if mqa != -1:
            name = name.replace('[M]', '', 1)  # Remove only first [M], if any
            name = name + '[M]'  # put [M] at the end
        return name

    def __fix_mqa(self,
                  path):  # Main Function that deletes fles allready in MQA folder and moves everything else in to it
        os.chdir(path)  # MQA Folder
        os.chdir("..")  # non MQA Folder
        for f in os.listdir(os.getcwd()):  # Pick each non MQA file to check against the MQA files
            if f[-5:] == ".flac":  # Check if the file is flac
                for m in os.listdir(path):  # Pick each MQA file to check against the non MQA
                    if f[:len(f) - 4] + "mqa.flac" == m:  # Check the no MQA file against the MQA file
                        if os.path.exists(os.path.join(os.getcwd(), f)):
                            try:
                                os.remove(os.path.join(os.getcwd(), f))  # removes the dublicate non MQA file
                            except OSError as error:
                                self.__write_error_log(error)
                            finally:
                                pass
            if os.path.isfile(os.path.join(os.getcwd(), f)):
                try:
                    shutil.move(os.path.join(os.getcwd(), f), os.path.join(path, f),
                                shutil.copy2)  # moves non found flacs in MQA Folder
                except OSError as error:
                    self.__write_error_log(error)
                finally:
                    pass
            else:
                if os.path.isfile(os.path.join(os.getcwd(), f)):
                    try:
                        shutil.move(os.path.join(os.getcwd(), f), os.path.join(path, f),
                                    shutil.copy2)  # moves non flacs in MQA Folder
                    except OSError as error:
                        self.__write_error_log(error)
                    finally:
                        pass

    def __mqa_fix(self):
        _path = askdirectory()  # Returns opened path as str
        if _path == "":
            _path = None
        else:  # Exit programm if user CANCELs the file open dialog
            for _root, subdirectories, files in os.walk(_path):
                _root = _root.replace('/', '\\')
                for subdirectory in subdirectories:
                    if subdirectory == "MQA":
                        self.__fix_mqa(os.path.join(_root, subdirectory))
            showinfo(title='Status', message='MQAs fixed successfully')
            self.status_str = "Done!"

    class RenameDialog(tk.Toplevel):
        def __init__(self):
            super().__init__()
            self.sbar_h = None
            self.list_index = []
            self.current = None
            self.new_name = None
            self.old_name = None
            self.old_word = ""
            self.new_word = ""
            self.rename = {'Old_Name': 'New_Name'}
            self.geometry('%dx%d+%d+%d' % (240, self.winfo_screenheight() / 1.6,
                                           self.winfo_screenwidth() / 4, self.winfo_screenheight() / 8))
            self.title('Add Rename Word')
            # self allow the variable to be used anywhere in the class

            frame1 = Frame(self)
            frame1.pack(fill=X)

            lbl1 = Label(frame1, text="Change", width=6)
            lbl1.pack(side=LEFT, padx=5, pady=10)

            self.entry1 = Entry(frame1)
            self.entry1.pack(fill=X, padx=5, expand=True)

            frame2 = Frame(self)
            frame2.pack(fill=X)

            lbl2 = Label(frame2, text="To", width=6)
            lbl2.pack(side=LEFT, padx=5, pady=10)

            self.entry2 = Entry(frame2)
            self.entry2.pack(fill=X, padx=5, expand=True)

            frame3 = Frame(self)
            frame3.pack(fill=X)

            # Command tells the form what to do when the button is clicked
            btn2 = Button(frame3, text="Close", command=self.on_done)
            btn2.pack(side=RIGHT, padx=10, pady=10)
            btn = Button(frame3, text="Submit", command=self.on_submit)
            btn.pack(side=RIGHT, padx=5, pady=10)

            self.frame4 = Frame(self, padx=5)
            self.frame4.pack()
            self.sbar = tk.Scrollbar(self.frame4)
            self.list = tk.Listbox(self.frame4, relief='sunken', fg='black', font='TkFixedFont',
                                   bg='lightyellow', height=0, width=28)
            self.sbar.config(command=self.list.yview)
            self.sbar.pack(side='right', fill='y')
            self.list.config(yscrollcommand=self.sbar.set)
            self.list.pack(expand=True, fill='both')
            self.sbar_h = tk.Scrollbar(self.frame4, orient='horizontal')
            self.sbar_h.config(command=self.list.xview)
            self.list.config(xscrollcommand=self.sbar_h.set)
            self.context = tk.Menu(self, tearoff=0)
            self.context.add_command(label='Modify', command=self.modify)
            self.context.add_command(label='Delete', command=self.delete)
            if self.tk.call('tk', 'windowingsystem') == 'aqua':
                self.bind('<2>', self.post)
            else:
                self.bind('<3>', self.post)
            create_beutify_file()
            old_name_list = []
            with open(os.path.join(os.getenv('LOCALAPPDATA'), 'beautify.csv'), encoding="utf-8", newline='') as csvfile:
                reader = csv.reader(csvfile)
                for r in reader:
                    self.rename[r[0]] = r[1]
                    old_name_list.append(len(r[0]))
            self.max_old_name = max(old_name_list)
            self.list_refresh()

        def list_refresh(self):
            if self.max_old_name < 13:
                self.max_old_name = 13
            if self.max_old_name > 13:
                self.sbar_h.pack(side='bottom', fill='x')
            if self.sbar_h and 13 >= self.max_old_name:
                self.sbar_h.pack_forget()
            self.list.delete(0, END)
            for self.list_index, (o, n) in enumerate(self.rename.items()):
                self.list.insert(self.list_index, ' ' + o + (self.max_old_name - len(o) + 2) * ' ' + n)

        def post(self, event):  # cascade menu
            self.context.post(event.x_root, event.y_root)

        def delete(self):
            self.current = self.list.curselection()[0]
            delete_item = list(self.rename.items())[self.current]
            self.rename.pop(delete_item[0])
            self.max_old_name = len(max(self.rename, key=len))
            self.list_refresh()

        def modify(self):
            self.current = self.list.curselection()[0]
            modify_item = list(self.rename.items())[self.current]
            self.entry1.delete(0, END)
            self.entry2.delete(0, END)
            self.entry1.insert(0, modify_item[0])
            self.entry2.insert(0, modify_item[1])

        def on_submit(self):
            self.old_word = self.entry1.get()
            self.new_word = self.entry2.get()
            if len(self.old_word) > self.max_old_name:
                self.max_old_name = len(self.old_word)
            self.list.insert(self.list.size(),
                             self.old_word + (self.max_old_name - len(self.old_word) + 2) * ' ' + self.new_word)
            self.rename[self.old_word] = self.new_word
            if self.old_word == self.new_word:
                self.rename.pop(self.old_word)
            self.list_refresh()

        def on_done(self):
            with open(os.path.join(os.getenv('LOCALAPPDATA'), 'beautify.csv'), 'w', encoding="utf-8",
                      newline='') as csvfile:
                fieldnames = ['Old_Name', 'New_Name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for old, new in self.rename.items():
                    writer.writerow({'Old_Name': old, 'New_Name': new})
            self.destroy()

    def __beautify(self, name):  # '''Beautify name'''
        name = name.replace("FLAC", '')
        name = name.replace("Flac", '')
        name = name.replace("EAC", '')
        name = name.replace("[]", '')
        name = name.replace("()", '')
        while name.find("  ") != -1:
            name = name.replace("  ", ' ')
        while name.find("- -") != -1:
            name = name.replace("- -", '-')
        while name.find("--") != -1:
            name = name.replace("--", '-')
        name = name.replace("-", ' - ')
        name = name.replace("_", ' ')
        while name.find("  ") != -1:
            name = name.replace("  ", ' ')
        name = name.strip()
        name = name.strip(".,- ")
        name = name.title()
        create_beutify_file()
        with open(os.path.join(os.getenv('LOCALAPPDATA'), 'beautify.csv'), encoding="utf-8", newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name = name.replace(row[0], row[1])
        return name


# Run main application
if __name__ == "__main__":
    root = tk.Tk()
    if darkdetect.isDark():
        style = darkstyle(root)
    FixEm(root)
    root.mainloop()
