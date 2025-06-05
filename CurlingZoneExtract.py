from tkinter import *
import tkinter as tk
from tkinter import ttk
import functions
import requests
from PIL import Image, ImageTk
import pathlib, os
import json


from bs4 import BeautifulSoup
import datetime
from dateutil import parser

root = Tk()

def print_entry_text():
    entry_text = entry.get()
    label.config(text='')
    label.config(text=entry_text)

    r = requests.get(entry_text, verify=False)



    global event_text
    event_text = ''


    #print(r.content)

    soup = BeautifulSoup(r.content, 'html5lib')
    #print(soup.prettify())

    global titlelist
    titlelist = []
# Find what the game is and get what type
    table2 = soup.find('div', attrs = {'class':'table-responsive'})
    print(table2)
    gametitle = table2.get_text()
    gametitle = gametitle.replace("Admin", "")
    gametitle = gametitle.replace('\n\t\t\t\t', '')
    titlelist.append(gametitle)
    #print(titlelist)


    gametype_label = tk.Label(root, text = "Game Type", font=('calibre',10,'bold'))
    gametype_label.place(x=10, y=140, relx=0.01, rely=0.01)

    gametitle_label = tk.Label(root, text='', font=('calibre', 10), bg='skyblue')
    gametitle_label.config(text=gametitle)
    #gametitle_label = tk.Label(root, text = gametitle, font=('calibre', 10), bg='skyblue')
    gametitle_label.place(x=100, y=140, relx=0.01, rely=0.01)

# Find Year from Soup
    year_raw = soup.find('div', attrs = {'class':'badge-widget'})
    year_raw_text = year_raw.get_text()
    year = year_raw_text[len(year_raw_text)-4:]

# Combine year with Datetime from Soup and Parse into a DT object
    linescorehead = soup.find('td', attrs = {'class':'linescorehead'})
    rawdate = linescorehead.get_text()
    rawdate2 = rawdate.replace("Draw", "")
    rawdate2 = year + rawdate2
    DT = parser.parse(rawdate2)


#Extract Year, Month, and Day from datetime object
    global gametime
    gametime = [DT.year, DT.month, DT.day]

    gamedate_label = tk.Label(root, text = "Game Date (Y/M/D)", font=('calibre',10,'bold'))
    gamedate_label.place(x=10, y=170, relx=0.01, rely=0.01)

    gamedatetext_label = tk.Label(root, text = str(gametime[0]) + "  " + str(gametime[1]) + "  " + str(gametime[2]) + "  ", font=('calibre', 10), bg='skyblue')
    gamedatetext_label.place(x=140, y=170, relx=0.01, rely=0.01)

    #print(gametime)

    linescoreheaddivs = soup.find_all('td', attrs = {'class':'linescorehead'})
    #print(linescoreheaddivs)


#SCOREBOARD HEADERS - HOW MANY ENDS IN THE GAME
    global scoreboard
    scoreboard = []
    ends = len(linescoreheaddivs)

    teamname_label = tk.Label(root, text = 'Team', font=('calibre', 10))
    teamname_label.place(x=60, y=220)
    hammer_label = tk.Label(root, text= "Hammer", font=('calibre', 10))
    hammer_label.place(x=150, y=220)
    end_label = tk.Label(root, text = "End", font=('calibre', 10))
    end_label.place(x=220, y=220)
    xplace = 260
    yplace = 220
    for x in range(2,ends-1):
        temp = str((linescoreheaddivs[x].get_text()))
        cleaned_temp = temp.replace('\xa0', '')
        scoreboard.append(cleaned_temp)

        temp_label = tk.Label(root, text = cleaned_temp, font=('calibre', 10), bg='skyblue')
        temp_label.place(x=xplace, y=yplace)
        xplace += 25



    #print(scoreboard)


    ###
### Find out what team starts with the hammer
    linescorehammer = soup.find_all('td', attrs = {'class': 'linescorehammer'})

    global hammerteamstart
    global endscoreteam1
    global endscoreteam2
    endscoreteam1 = []
    endscoreteam2 = []
    hammerteamstart = []

    if linescorehammer[0] == '<td align="center" class="linescorehammer"><img src="https://www.curlingzone.com/forums/images/hammer.gif" style="height: 15px; width: 15px;"/></td>':
        starthammer = 1
        hammerteamstart.append(1)
    else:
        starthammer = 2
        hammerteamstart.append(2)




    img_file_name = "hammer_icon.jpg"
    current_dir = pathlib.Path(__file__).parent.resolve() # current directory
    img_path = os.path.join(current_dir, img_file_name)
    hammer_image = Image.open(img_path)
    itkresized = hammer_image.resize((15,15))
    global itk
    itk = ImageTk.PhotoImage(itkresized)
    hammer_panel = ttk.Label(root, image = itk)
    if hammerteamstart[0] == 1:
        hammer_panel.place(x=170, y=250)
    if hammerteamstart[0] == 2:
        hammer_panel.place(x=170, y=280)

    linescoreteamdivs = soup.find_all('td', attrs = {'class':'linescoreteam'})

    linescoreenddivs = soup.find_all('td', attrs = {'class':'linescoreend'})

    linescorefinaldivs = soup.find_all('td', attrs = {'class':'linescorefinal'})

    xplace=260
    yplace=250
    for x in range(0,len(scoreboard)):
        temp = linescoreenddivs[x].get_text()
        temp = temp.replace('\xa0', '')
        endscoreteam1.append(temp)
        temp_label = ttk.Label(root, text=temp, font=('calibre', 10))
        temp_label.place(x=xplace, y=yplace)
        xplace += 25

    xplace=260
    yplace=280
    for x in range(len(scoreboard), len(scoreboard)+len(scoreboard)):
        temp = linescoreenddivs[x].get_text()
        temp = temp.replace('\xa0', '')
        endscoreteam2.append(temp)
        temp_label = ttk.Label(root, text=temp, font=('calibre', 10))
        temp_label.place(x=xplace, y=yplace)
        xplace += 25

    #print(scoreboard)
    #print(hammerteamstart)
    #print(endscoreteam1)
    #print(endscoreteam2)

    linescoreteamlinks = soup.find_all('a', attrs = {'class':'linescoreteamlink'})

    global teamnames
    teamnames = []
    for x in linescoreteamlinks:
        teamnames.append(x)

    teamnames[0] = teamnames[0].get_text()
    teamnames[1] = teamnames[1].get_text()

    team1 = teamnames[0]
    team2 = teamnames[1]

    teamlocations = []
    for x in range(len(linescoreteamdivs)):
        y = linescoreteamdivs[x].get_text()
        y = y.replace(teamnames[x], "")
        teamlocations.append(y)

    global teamlocation1
    global teamlocation2
    teamlocation1 = teamlocations[0]
    teamlocation2 = teamlocations[1]

    countrylist = ['Norway', 'Japan', 'Canada', 'Austria', 'China', 'Czechia', 'Germany', 'Italy', 'Korea', 'Norway', 'Scotland', 'Sweden', 'Switzerland', 'United States']

    if team1 in countrylist:
        tempteam = team1
        team1=teamlocation1
        teamlocation1=tempteam

    if team2 in countrylist:
        tempteam = team2
        team2=teamlocation2
        teamlocation2 = tempteam

    #print(team1)
    #print(teamlocation1)

    #print(team2)
    #print(teamlocation2)

    team1_label = tk.Label(root, text = team1, font=('calibre', 10))
    team1_label.place(x=40, y=250)
    team2_label = tk.Label(root, text = team2, font=('calibre', 10))
    team2_label.place(x=40, y=280)

    global finalscores
    finalscores = []
    for x in linescorefinaldivs:
        finalscores.append(x.get_text())

    for x in range(len(finalscores)):
        finalscores[x] = finalscores[x].replace('\xa0', '')

    #print(finalscores)


    final_label = tk.Label(root, text = "Final", font=('calibre', 10))
    final_label.place(x=xplace+25, y=220)

    finalscore1_label = tk.Label(root, text=finalscores[0], font=('calibre', 10), bg='skyblue')
    finalscore1_label.place(x=xplace+25, y=250)

    finalscore2_label = tk.Label(root, text=finalscores[1], font=('calibre', 10))
    finalscore2_label.place(x=xplace+25, y=280)

    countryabbrv = ['Kor', 'KOR', 'Jpn', 'JPN']
    countrydict = {
        'Kor':'Korea',
        'KOR':'Korea',
        'Jpn':'Japan',
        'JPN':'Japan'}

    for x in countryabbrv:
        if x in teamlocation1:
            teamlocation1 = countrydict[x]
        if x in teamlocation2:
            teamlocation2 = countrydict[x]

    teamlocation_label = tk.Label(root, text = "Representing", font=('calibre', 10))
    teamlocation_label.place(x=xplace+80, y=220)

    teamlocation1_label = tk.Label(root, text = teamlocation1, font=('calibre', 10))
    teamlocation1_label.place(x=xplace+80, y=250)

    teamlocation2_label = tk.Label(root, text = teamlocation2, font=('calibre', 10))
    teamlocation2_label.place(x=xplace+80, y=280)

    #print(teamlocation1)
    #print(teamlocation2)

    global hammerteamend
    hammerteamend=[]
    hammerteamend.append(hammerteamstart[0])

    for x in range(1,len(endscoreteam1)):
        hammerteamend.append(0)

    currenthammer = hammerteamstart[0]

    for x in range(len(endscoreteam1)-1):
        if endscoreteam1[x] == "0":
            if endscoreteam2[x] == "0":
                currenthammer = currenthammer
                hammerteamend[x+1]=currenthammer

        if endscoreteam1[x] != "0" and endscoreteam2[x] == "0":
            currenthammer = 2
            hammerteamend[x+1] = currenthammer

        if endscoreteam1[x] == "0" and endscoreteam2[x] != "0":
            currenthammer = 1
            hammerteamend[x+1] = currenthammer


    for x in range(0, len(hammerteamend)):
        if hammerteamend[x] == 0:
            hammerteamend[x] = 'X'

    xplace=260
    yplace=330
    for x in range(0,len(hammerteamend)):

        temp_label = ttk.Label(root, text=hammerteamend[x], font=('calibre', 10))
        temp_label.place(x=xplace, y=yplace)
        xplace += 25



    #print(hammerteamend)

    hammerteamend_label = tk.Label(root, text = "Hammer Team", font=('calibre', 10))
    hammerteamend_label.place(x=150, y=330)

    #######
    ####### POSITIONS
    #######

    Positions = []
    Names = []

    First = True
    for x in soup.find_all(string='Skip'):
            if First == True:
                Positions.append(x)
                name = x.find_all_next('b')

                stringname = (str(name[0]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                temp = name[1].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                stringname= (str(name[2]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                temp = name[3].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                stringname= (str(name[4]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                temp = name[5].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                stringname= (str(name[6]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                temp = name[7].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                stringname= (str(name[8]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)


                temp = name[9].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                stringname= (str(name[10]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                temp = name[11].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                stringname= (str(name[12]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                stringname= (str(name[14]))
                temp = stringname.replace('<b>', '')
                temp = temp.replace('<br/>', ' ')
                temp = temp.replace('</b>', '')
                Names.append(temp)

                temp = name[13].get_text()
                temp = temp.replace(': ', '')
                Positions.append(temp)

                First = False

    print(Positions)
    print(Names)


    PositionsAlt = []
    NamesAlt = []

    First = True
    for x in soup.find_all(string="Fourth: "):
        if First == True:
            temp = x.replace(': ', '')
            PositionsAlt.append(temp)
            name = x.find_all_next('b')

            stringname = (str(name[0]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[1].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[2]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[3].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[4]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[5].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[6]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[7].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[8]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[9].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[10]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[11].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[12]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            temp = name[13].get_text()
            temp = temp.replace(': ', '')
            PositionsAlt.append(temp)

            stringname= (str(name[14]))
            temp = stringname.replace('<b>', '')
            temp = temp.replace('<br/>', ' ')
            temp = temp.replace('</b>', '')
            NamesAlt.append(temp)

            First = False


    #print(PositionsAlt)
    #print(NamesAlt)



    # Label
    format_label = tk.Label(root, text="Select Position Format", font=('calibre', 10, 'bold'))
    format_label.place(x=25, y=360)

    # Dropdown for format selection
    position_format = tk.StringVar()
    format_combo = ttk.Combobox(root, textvariable=position_format, state='readonly')
    format_combo['values'] = ('Default Format', 'Alternate Format')
    format_combo.place(x=25, y=390)
    format_combo.current(0)  # Set initial selection

    # Frame to hold player display (makes it easier to update)
    player_display_frame = tk.Frame(root)
    player_display_frame.place(x=200, y=380)

    # Function to update the display when dropdown changes
    def on_format_change(event=None):
        # Clear the frame
        for widget in player_display_frame.winfo_children():
            widget.destroy()

        # Get selection
        selected_format = position_format.get()
        if selected_format == 'Default Format':

            global selected_names
            global selected_positions
            selected_positions = Positions
            selected_names = Names
        else:
            selected_positions = PositionsAlt
            selected_names = NamesAlt

        # Header
        tk.Label(player_display_frame, text="Selected Positions & Players:", font=('calibre', 10, 'bold')).pack(anchor='w')

        # Display positions and players
        for i in range(len(selected_names)):
            pos = selected_positions[i] if i < len(selected_positions) else "N/A"
            name = selected_names[i]
            display_text = f"{pos}: {name}"
            tk.Label(player_display_frame, text=display_text, font=('calibre', 10)).pack(anchor='w')\

        print(selected_names, selected_positions)
        return selected_positions, selected_names

    # Bind selection change to function
    format_combo.bind("<<ComboboxSelected>>", on_format_change)

    # Show default format initially
    on_format_change()

    return(titlelist, gametime, scoreboard, hammerteamstart, endscoreteam1, endscoreteam2, teamnames, teamlocation1, teamlocation2, finalscores, hammerteamend)

def export_data():

    event_text = event.get()
    file_text = file.get()

    print(event_text)
    print(titlelist)
    print(gametime)
    print(scoreboard)
    print(hammerteamstart)
    print(endscoreteam1)
    print(endscoreteam2)
    print(hammerteamend)
    print(teamnames)
    print(teamlocation1)
    print(teamlocation2)
    print(selected_positions)
    print(selected_names)

    # Structured dictionary
    match_data = {
        'event': event_text,
        "date": {
            "year": gametime[0],
            "month": gametime[1],
            "day": gametime[2]
        },
        "ends": scoreboard,
        "hammerstart": hammerteamstart,
        "score_by_end": {
            'Team1' : endscoreteam1,
            'Team2': endscoreteam2
        },
        "hammerteamend": hammerteamend,
        'FinalScore1' : finalscores[0],
        'FinalScore2' : finalscores[1],
        "TeamName1" : teamnames[0],
        "TeamName2" : teamnames[1],
        "TeamLocation1" : teamlocation1,
        "TeamLocation2" : teamlocation2,
        'Team1Players': {
            "Fourth" : selected_names[0],
            "Third": selected_names[1],
            "Second": selected_names[2],
            "First": selected_names[3]
            },
        'Team2Players': {
            "Fourth": selected_names[4],
            "Third": selected_names[5],
            "Second": selected_names[6],
            "First": selected_names[7]
            }

    }

# Export to JSON
    with open(file_text + '.json', "w", encoding="utf-8") as f:
        json.dump(match_data, f, indent=4)



root.title("Curling Zone Game Data Extraction")

root.geometry("900x600")
root.config(bg="skyblue")

game_URL = tk.StringVar()


entry_label = tk.Label(root, text = 'Curling Zone Game URL', font=('calibre',10, 'bold'))
entry_label.place(x=10,  y=60,  relx=0.01,  rely=0.01)
entry = ttk.Entry(root, textvariable = game_URL, font=('calibre', 10, 'normal'), width=100)
entry.place(x=180, y=60, relx=0.01, rely=0.01)
entry.focus()

event_name = tk.StringVar()
event_label = tk.Label(root, text = 'Event Name', font=('calibre',10, 'bold'))
event_label.place(x=180,  y=140,  relx=0.01,  rely=0.01)
event = ttk.Entry(root, textvariable = event_name, font=('calibre', 10, 'normal'), width=100)
event.place(x=260, y=140, relx=0.01, rely=0.01)

file_name = tk.StringVar()
file_label = tk.Label(root, text = 'File Name', font=('calibre',10, 'bold'))
file_label.place(x=220,  y=170,  relx=0.01,  rely=0.01)
file = ttk.Entry(root, textvariable = file_name, font=('calibre', 10, 'normal'), width=100)
file.place(x=300, y=170, relx=0.01, rely=0.01)



button = tk.Button(root, text="Load Game URL",
                   command=print_entry_text)
button.place(x=70, y=90, relx=0.01, rely=0.01)

label = tk.Label(root, text="")
label.place(x=100, y=40, relx=0.1, rely=0.1)

exportbutton = tk.Button(root, text="Export Data to JSON",
                   command=export_data)
exportbutton.place(x=25, y=480, relx=0.01, rely=0.01)

label = tk.Label(root, text="")
label.place(x=100, y=40, relx=0.1, rely=0.1)


root.mainloop()


