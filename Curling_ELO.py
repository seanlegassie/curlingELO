import json
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox, Spinbox


START_ELO = 1000.0
K_FACTOR = 32


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400.0))

def update_elo(rating_a, rating_b, score_a):
    exp_a = expected_score(rating_a, rating_b)
    rating_a += K_FACTOR * (score_a - exp_a)
    rating_b += K_FACTOR * ((1 - score_a) - (1 - exp_a))
    return rating_a, rating_b

def process_matches(match_data_list):
    match_data_list.sort(key=lambda m: (m['date']['year'], m['date']['month'], m['date']['day']))
    ratings = {}
    games_played = {}
    for match in match_data_list:
        team1 = [match['Team1Players'].get(pos) for pos in ['Fourth','Third','Second','First']]
        team2 = [match['Team2Players'].get(pos) for pos in ['Fourth','Third','Second','First']]
        score1, score2 = int(match.get('FinalScore1', 0)), int(match.get('FinalScore2', 0))
        outcome = 1 if score1 > score2 else (0 if score2 > score1 else 0.5)
        for p1 in team1:
            for p2 in team2:
                if p1 and p2:
                    r1 = ratings.get(p1, START_ELO)
                    r2 = ratings.get(p2, START_ELO)
                    new_r1, new_r2 = update_elo(r1, r2, outcome)
                    ratings[p1] = new_r1
                    ratings[p2] = new_r2
                    games_played[p1] = games_played.get(p1, 0) + 1
                    games_played[p2] = games_played.get(p2, 0) + 1
    for player in games_played:
        games_played[player] = games_played[player] // 4
    return ratings, games_played

def get_latest_rating(ratings, player):
    return ratings.get(player, START_ELO)

def predict_team_win_prob(ratings, team1, team2, weights):
    r1 = sum(get_latest_rating(ratings, p) * w for p, w in zip(team1, weights)) / sum(weights)
    r2 = sum(get_latest_rating(ratings, p) * w for p, w in zip(team2, weights)) / sum(weights)
    return 1.0 / (1.0 + 10 ** ((r2 - r1) / 400.0))

class WHRApp(tk.Tk):
    def __init__(self, ratings, games_played):
        super().__init__()
        self.title("Curling Elo Predictor")
        self.ratings = ratings
        self.games_played = games_played
        self.players = sorted(ratings.keys())

        self.positions = ['Fourth', 'Third', 'Second', 'Lead']
        self.team_a_selectors = {}
        self.team_b_selectors = {}
        self.weights = {}

        tk.Label(self, text="Team A", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(self, text="Team B", font=('Arial', 12, 'bold')).grid(row=0, column=2, padx=10, pady=5)
        tk.Label(self, text="Weight", font=('Arial', 12, 'bold')).grid(row=0, column=4, padx=10, pady=5)

        for idx, pos in enumerate(self.positions):
            tk.Label(self, text=pos).grid(row=idx+1, column=0, sticky='e')
            self.team_a_selectors[pos] = self.create_searchable_combobox(row=idx+1, column=1)

            tk.Label(self, text=pos).grid(row=idx+1, column=2, sticky='e')
            self.team_b_selectors[pos] = self.create_searchable_combobox(row=idx+1, column=3)

            self.weights[pos] = tk.DoubleVar(value=1.0)
            Spinbox(self, from_=0.0, to=10.0, increment=0.1, textvariable=self.weights[pos], width=5).grid(row=idx+1, column=4)

        tk.Button(self, text="Predict", command=self.on_predict).grid(row=6, column=0, columnspan=5, pady=15)
        tk.Button(self, text="Load Team CSV", command=self.load_teams_from_csv).grid(row=7, column=0, columnspan=5, pady=5)

        self.filter_games_var = tk.IntVar()
        tk.Checkbutton(self, text="Show only players with games played", variable=self.filter_games_var, command=self.populate_ratings).grid(row=8, column=0, columnspan=2)

        tk.Label(self, text="Min games:").grid(row=8, column=2, sticky='e')
        self.min_games_spin = Spinbox(self, from_=0, to=100, width=5)
        self.min_games_spin.grid(row=8, column=3, sticky='w')
        self.min_games_spin.delete(0, tk.END)
        self.min_games_spin.insert(0, "0")

        self.ratings_frame = tk.Frame(self)
        self.ratings_frame.grid(row=0, column=5, rowspan=9, sticky='ns', padx=10, pady=5)

        self.scrollbar = tk.Scrollbar(self.ratings_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.ratings_listbox = tk.Listbox(self.ratings_frame, width=30, height=20, yscrollcommand=self.scrollbar.set)
        self.ratings_listbox.pack(side='left', fill='y')
        self.scrollbar.config(command=self.ratings_listbox.yview)

        self.teams_output = tk.Text(self, width=70, height=15)
        self.teams_output.grid(row=9, column=0, columnspan=6, padx=10, pady=10)

        self.populate_ratings()

    def create_searchable_combobox(self, row, column):
        combo = Combobox(self, values=self.players, width=25)
        combo.grid(row=row, column=column, padx=5, pady=3)
        combo.set('')
        combo.bind('<KeyRelease>', lambda event: self.filter_combobox(combo))
        return combo

    def filter_combobox(self, combo):
        value = combo.get().lower()
        if value == '':
            combo['values'] = self.players
        else:
            filtered = [p for p in self.players if value in p.lower()]
            combo['values'] = filtered

    def on_predict(self):
        team_a = [cb.get() for cb in self.team_a_selectors.values() if cb.get()]
        team_b = [cb.get() for cb in self.team_b_selectors.values() if cb.get()]
        weights = [self.weights[pos].get() for pos in self.positions]

        if len(team_a) != 4 or len(team_b) != 4:
            messagebox.showwarning("Selection Error", "Please select all four players for both teams.")
            return

        prob = predict_team_win_prob(self.ratings, team_a, team_b, weights)
        messagebox.showinfo("Prediction", f"Probability Team A wins: {prob:.2%}\nTeam B wins: {(1-prob):.2%}")

    def populate_ratings(self):
        self.ratings_listbox.delete(0, tk.END)
        min_games = int(self.min_games_spin.get())
        for player in sorted(self.ratings, key=lambda x: -self.ratings[x]):
            if self.games_played.get(player, 0) < min_games:
                continue
            self.ratings_listbox.insert(tk.END, f"{player}: {self.ratings[player]:.2f}")

    def load_teams_from_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        self.teams_output.delete(1.0, tk.END)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 5:
                    team_name = row[0].strip()
                    players = [row[i].strip() for i in range(1, 5)]
                    ratings = [(p, get_latest_rating(self.ratings, p)) for p in players]
                    ratings.sort(key=lambda x: -x[1])
                    total = sum(r for _, r in ratings)
                    avg = total / len(ratings)
                    self.teams_output.insert(tk.END, f"Team: {team_name}\n")
                    for player, rating in ratings:
                        self.teams_output.insert(tk.END, f"  {player}: {rating:.2f}\n")
                    self.teams_output.insert(tk.END, f"  Total Rating: {total:.2f}\n  Average Rating: {avg:.2f}\n\n")


if __name__ == "__main__":
    match_data = []
    dirname = filedialog.askdirectory(title="Select Match JSON Directory")
    if dirname:
        import os
        for root, _, files in os.walk(dirname):
            for file in files:
                if file.endswith(".json"):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        match_data.append(json.load(f))
    else:
        messagebox.showerror("No Directory", "No directory selected. Exiting.")
        exit(1)

    ratings, games_played = process_matches(match_data)
    app = WHRApp(ratings, games_played)
    app.mainloop()
