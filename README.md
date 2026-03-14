# Album Fix
## uniformly format the folder name of each Album of your music collection

*Instructions:*

The main program's function is to uniformly format the folder name of each Album.
The formatting it attempts to do is unter this pattern:
Release Date. Album Name. Further information, if any. e.g.:
**1978. Bloody Tourists (1996)**
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
