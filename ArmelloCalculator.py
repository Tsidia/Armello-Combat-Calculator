import tkinter as tk
from tkinter import messagebox
import random

def roll_dice(dice_count, is_day, explode_pool, initial_hits, initial_defends, is_opponent_king):
    outcomes = {'hit': initial_hits, 'defend': initial_defends}
    additional_rolls = 0

    while dice_count > 0:
        dice_count -= 1
        roll = random.choice(['Sword', 'Shield', 'Sun', 'Moon', 'Worm', 'Wyrm'])

        if roll == 'Sword' or roll == 'Wyrm':
            outcomes['hit'] += 1
        elif roll == 'Shield':
            outcomes['defend'] += 1
        elif (roll == 'Sun' and is_day) or (roll == 'Moon' and not is_day):
            outcomes['hit'] += 1
        elif roll == 'Worm' and is_opponent_king:
            outcomes['defend'] += 1
        else:
            additional_rolls += 1

        if roll == 'Wyrm' and explode_pool > 0:
            dice_count += 1
            explode_pool -= 1

    return outcomes, additional_rolls

def armello_combat_probabilities(dice_a, dice_b, hp_a, hp_b, explode_pool_a, explode_pool_b, is_day, initial_hits_a, initial_defends_a, initial_hits_b, initial_defends_b, is_fighting_king, samples=100000):
    outcomes = {'both_survive': 0, 'both_die': 0, 'a_kills_b': 0, 'b_kills_a': 0}

    for _ in range(samples):
        result_a, extra_rolls_for_king = roll_dice(dice_a, is_day, explode_pool_a, initial_hits_a, initial_defends_a, False)
        king_dice_b = dice_b + extra_rolls_for_king if is_fighting_king else dice_b
        result_b, _ = roll_dice(king_dice_b, is_day, explode_pool_b, initial_hits_b, initial_defends_b, is_fighting_king)

        damage_to_b = max(0, result_a['hit'] - result_b['defend'])
        damage_to_a = max(0, result_b['hit'] - result_a['defend'])

        new_hp_a = hp_a - damage_to_a
        new_hp_b = hp_b - damage_to_b

        if new_hp_a <= 0 and new_hp_b <= 0:
            outcomes['both_die'] += 1
        elif new_hp_a <= 0:
            outcomes['b_kills_a'] += 1
        elif new_hp_b <= 0:
            outcomes['a_kills_b'] += 1
        else:
            outcomes['both_survive'] += 1

    probabilities = {outcome: (count / samples) * 100 for outcome, count in outcomes.items()}

    return probabilities

class ArmelloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Armello Combat Simulator")

        # Labels and Entries for Player A
        tk.Label(root, text="Player A").grid(row=0, column=0, pady=10)
        self.dice_a = self.create_entry("Number of dice:", 1)
        self.hp_a = self.create_entry("Health points:", 2)
        self.explode_pool_a = self.create_entry("Explode pool:", 3)
        self.initial_hits_a = self.create_entry("Initial hits:", 4)
        self.initial_defends_a = self.create_entry("Initial defends:", 5)

        # Labels and Entries for Player B
        tk.Label(root, text="Player B").grid(row=0, column=2, pady=10)
        self.dice_b = self.create_entry("Number of dice:", 1, col=2)
        self.hp_b = self.create_entry("Health points:", 2, col=2)
        self.explode_pool_b = self.create_entry("Explode pool:", 3, col=2)
        self.initial_hits_b = self.create_entry("Initial hits:", 4, col=2)
        self.initial_defends_b = self.create_entry("Initial defends:", 5, col=2)

        # Fighting King Checkbox
        self.is_fighting_king = tk.BooleanVar()
        tk.Checkbutton(root, text="Is the opponent the King?", variable=self.is_fighting_king).grid(row=6, columnspan=3, pady=10)

        # Submit Button
        tk.Button(root, text="Calculate Probabilities", command=self.calculate_probabilities).grid(row=7, columnspan=3, pady=10)

    def create_entry(self, label_text, row, col=1):
        tk.Label(self.root, text=label_text).grid(row=row, column=col-1, padx=5, pady=5, sticky=tk.E)
        entry = tk.Entry(self.root)
        entry.grid(row=row, column=col, padx=5, pady=5)
        return entry

    def calculate_probabilities(self):
        try:
            dice_a = int(self.dice_a.get())
            hp_a = int(self.hp_a.get())
            explode_pool_a = int(self.explode_pool_a.get())
            initial_hits_a = int(self.initial_hits_a.get())
            initial_defends_a = int(self.initial_defends_a.get())

            dice_b = int(self.dice_b.get())
            hp_b = int(self.hp_b.get())
            explode_pool_b = int(self.explode_pool_b.get())
            initial_hits_b = int(self.initial_hits_b.get())
            initial_defends_b = int(self.initial_defends_b.get())

            is_fighting_king = self.is_fighting_king.get()
            is_day = True

            probabilities = armello_combat_probabilities(dice_a, dice_b, hp_a, hp_b, explode_pool_a, explode_pool_b, is_day, initial_hits_a, initial_defends_a, initial_hits_b, initial_defends_b, is_fighting_king)
            result = "\n".join([f"{outcome}: {probability:.2f}%" for outcome, probability in probabilities.items()])
            messagebox.showinfo("Combat Outcome Probabilities", result)

        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid integers for all inputs.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArmelloApp(root)
    root.mainloop()
