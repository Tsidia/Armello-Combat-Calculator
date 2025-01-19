import tkinter as tk
from tkinter import ttk
import random

def roll_armello_die(is_day, is_king=False):
    """
    Roll a single Armello die.
    
    Return a tuple: (hits, defends, extra_roll)
      - hits: number of hits generated by this single die
      - defends: number of defends generated by this single die
      - extra_roll: True if this die grants an extra roll (Wyld), False otherwise
    """
    # Die faces: ["Sword", "Shield", "Sun", "Moon", "Worm", "Wyld"]
    face = random.choice(["Sword", "Shield", "Sun", "Moon", "Worm", "Wyld"])
    
    # Default outcomes
    hits = 0
    defends = 0
    extra_roll = False
    
    if face == "Sword":
        # 1 hit
        hits = 1
    elif face == "Shield":
        # 1 defend
        defends = 1
    elif face == "Sun":
        # 1 hit if day, else 0
        if is_day:
            hits = 1
        else:
            # Miss if night
            if is_king:
                # In King scenario, this might let the King roll an extra die *if the player is the one missing*.
                pass
    elif face == "Moon":
        # 1 hit if night, else 0
        if not is_day:
            hits = 1
        else:
            # Miss if day
            if is_king:
                pass
    elif face == "Worm":
        # Normally does nothing, but if is_king=True (King rolling):
        # the King gets 1 defend from a Worm
        if is_king:
            defends = 1
    elif face == "Wyld":
        # 1 hit + explode (extra roll) as long as under explode pool limit
        hits = 1
        extra_roll = True
    
    return hits, defends, extra_roll

def simulate_rolls(num_dice, explode_pool, guaranteed_hits, guaranteed_defends, is_day, is_king=False):
    """
    Simulate the total dice rolls (including explosions from Wyld) for one side.
    
    Returns a tuple (total_hits, total_defends).
    """
    total_hits = guaranteed_hits
    total_defends = guaranteed_defends
    
    dice_to_roll = num_dice
    extra_rolls_used = 0
    
    while dice_to_roll > 0:
        hits, defends, extra_roll = roll_armello_die(is_day=is_day, is_king=is_king)
        total_hits += hits
        total_defends += defends
        
        # If Wyld, check if we can still use the explode
        if extra_roll and extra_rolls_used < explode_pool:
            extra_rolls_used += 1
            # We gain 1 extra die to roll
            dice_to_roll += 1
        
        dice_to_roll -= 1
    
    return total_hits, total_defends

def simulate_single_battle(
    # Player (attacker) stats
    p_dice, p_health, p_explode, p_guaranteed_hits, p_guaranteed_def, 
    # Opponent (defender) stats
    e_dice, e_health, e_explode, e_guaranteed_hits, e_guaranteed_def, 
    # General options
    is_day, is_king=False
):
    """
    Simulate a single battle scenario.
    Return a tuple (player_survives, enemy_survives).
    
    Special King rules:
    - King rolling: Worm -> 1 defend (already handled in roll_armello_die with is_king=True).
    - Player misses: King gets 1 more die roll, ignoring the King's explode pool limit.
    """
    
    # ========================
    # Player's rolling phase
    # ========================
    # The player might get multiple dice due to Wyld, 
    # but also the King might get "bonus" dice if the player *misses*.
    
    # We'll keep track of how many dice the player has to roll "right now",
    # plus how many times the player can still explode (Wyld).
    
    p_total_hits = p_guaranteed_hits
    p_total_defends = p_guaranteed_def
    
    e_total_hits = e_guaranteed_hits
    e_total_defends = e_guaranteed_def
    
    # If it's the King scenario, we'll handle the King's extra dice from the player's misses.
    # We'll store the King's dice in e_dice and e_explode (like normal), 
    # but King can also earn extra dice from the player's misses.
    
    # Let's define a small function to do the actual rolling for the player,
    # but also track which dice are "misses" so that the King can roll 1 extra die per miss.
    def roll_for_player(num_dice, explode_pool):
        total_h = 0
        total_d = 0
        dice_to_roll = num_dice
        extra_used = 0
        
        misses = 0  # track how many misses if is_king is True
        
        while dice_to_roll > 0:
            face = random.choice(["Sword", "Shield", "Sun", "Moon", "Worm", "Wyld"])
            
            hits = 0
            defends = 0
            extra_roll = False
            
            if face == "Sword":
                hits = 1
            elif face == "Shield":
                defends = 1
            elif face == "Sun":
                if is_day:
                    hits = 1
                else:
                    # miss
                    if is_king: 
                        misses += 1
            elif face == "Moon":
                if not is_day:
                    hits = 1
                else:
                    # miss
                    if is_king:
                        misses += 1
            elif face == "Worm":
                # Normal scenario: does nothing for the player
                # If the player is the one rolling, there's no special effect 
                # for the player if is_king==True. 
                # (The King's worms are special for the King, not the player.)
                if is_king:
                    misses += 1
            elif face == "Wyld":
                hits = 1
                extra_roll = True
            
            total_h += hits
            total_d += defends
            
            if extra_roll and extra_used < explode_pool:
                extra_used += 1
                dice_to_roll += 1
            
            dice_to_roll -= 1
        
        return total_h, total_d, misses
    
    if not is_king:
        # Player vs. Player scenario: straightforward
        p_hits, p_defends = simulate_rolls(
            p_dice, p_explode, p_guaranteed_hits, p_guaranteed_def, is_day, is_king=False
        )
        e_hits, e_defends = simulate_rolls(
            e_dice, e_explode, e_guaranteed_hits, e_guaranteed_def, is_day, is_king=False
        )
        # Calculate net damage
        dmg_to_enemy = p_hits - e_defends
        dmg_to_player = e_hits - p_defends
        
        # Apply damage
        p_final_health = p_health - max(0, dmg_to_player)
        e_final_health = e_health - max(0, dmg_to_enemy)
        
        player_survives = (p_final_health >= 1)
        enemy_survives = (e_final_health >= 1)
    
    else:
        # Player vs. King scenario
        # 1) Player's dice roll with possible misses awarding King extra dice
        p_hits, p_defends, p_misses = roll_for_player(p_dice, p_explode)
        
        # Add guaranteed hits/defends because we haven't added them yet
        p_total_hits = p_hits
        p_total_defends = p_defends
        
        # 2) King rolls e_dice normally, but also gets +1 die per player miss (p_misses),
        #    ignoring the king's explode pool limit for these bonus dice.
        #    Also, each worm for the King is 1 defend (already handled in roll_armello_die if is_king=True).
        
        # We create a function to roll dice for the King, but the King can exceed explode_pool with the bonus dice.
        def roll_for_king(base_dice, extra_bonus_dice, explode_pool):
            total_h = 0
            total_d = 0
            dice_to_roll = base_dice + extra_bonus_dice
            extra_used = 0
            
            while dice_to_roll > 0:
                hits, defends, extra_roll = roll_armello_die(is_day, is_king=True)
                total_h += hits
                total_d += defends
                # If Wyld, can explode up to explode_pool
                if extra_roll and extra_used < explode_pool:
                    extra_used += 1
                    dice_to_roll += 1
                dice_to_roll -= 1
            
            return total_h, total_d
        
        e_hits, e_defends = roll_for_king(e_dice, p_misses, e_explode)
        
        # Add the King's guaranteed hits/defends
        e_hits += e_guaranteed_hits
        e_defends += e_guaranteed_def
        
        # Compute damage
        dmg_to_king = p_total_hits - e_defends
        dmg_to_player = e_hits - p_total_defends
        
        p_final_health = p_health - max(0, dmg_to_player)
        e_final_health = e_health - max(0, dmg_to_king)
        
        player_survives = (p_final_health >= 1)
        enemy_survives = (e_final_health >= 1)
    
    return (player_survives, enemy_survives)


def run_monte_carlo(
    iterations,
    p_dice, p_health, p_explode, p_guaranteed_hits, p_guaranteed_def,
    e_dice, e_health, e_explode, e_guaranteed_hits, e_guaranteed_def,
    is_day, is_king
):
    """
    Run the Monte Carlo simulation (given number of iterations) and
    return the probabilities of each outcome:
      - Player kills enemy, survives
      - Enemy kills player, survives
      - Both survive
      - Both die
    """
    
    outcome_counts = {
        "p_win": 0,        # Player kills enemy, survives
        "e_win": 0,        # Enemy kills player, survives
        "both_survive": 0, # Both survive
        "both_die": 0      # Both die
    }
    
    for _ in range(iterations):
        p_survives, e_survives = simulate_single_battle(
            p_dice, p_health, p_explode, p_guaranteed_hits, p_guaranteed_def, 
            e_dice, e_health, e_explode, e_guaranteed_hits, e_guaranteed_def, 
            is_day, is_king
        )
        
        if p_survives and (not e_survives):
            outcome_counts["p_win"] += 1
        elif (not p_survives) and e_survives:
            outcome_counts["e_win"] += 1
        elif p_survives and e_survives:
            outcome_counts["both_survive"] += 1
        else:
            # not p_survives and not e_survives
            outcome_counts["both_die"] += 1
    
    # Convert counts to percentages
    p_win_pct = 100.0 * outcome_counts["p_win"] / iterations
    e_win_pct = 100.0 * outcome_counts["e_win"] / iterations
    both_survive_pct = 100.0 * outcome_counts["both_survive"] / iterations
    both_die_pct = 100.0 * outcome_counts["both_die"] / iterations
    
    return (p_win_pct, e_win_pct, both_survive_pct, both_die_pct)


# ---------------------
# Tkinter GUI
# ---------------------

class ArmelloCombatSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Armello Combat Simulator")
        
        # Create input fields
        # We'll place them in a grid for neatness
        row_idx = 0
        
        # Iterations
        tk.Label(self, text="Number of Simulations").grid(row=row_idx, column=0, sticky=tk.E)
        self.iterations_var = tk.IntVar(value=10000)
        tk.Entry(self, textvariable=self.iterations_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        # Day/Night
        tk.Label(self, text="Time of Day").grid(row=row_idx, column=0, sticky=tk.E)
        self.day_night_var = tk.StringVar(value="Day")
        ttk.Combobox(self, textvariable=self.day_night_var, values=["Day", "Night"], width=7).grid(row=row_idx, column=1)
        row_idx += 1
        
        # Is King or not
        tk.Label(self, text="Battle Type").grid(row=row_idx, column=0, sticky=tk.E)
        self.king_var = tk.BooleanVar(value=False)
        cb_king = ttk.Combobox(
            self, 
            values=["Player vs Player", "Player vs King"], 
            width=15
        )
        cb_king.current(0)
        cb_king.grid(row=row_idx, column=1)
        
        def on_king_combo_change(event):
            choice = cb_king.get()
            if choice == "Player vs King":
                self.king_var.set(True)
            else:
                self.king_var.set(False)
        cb_king.bind("<<ComboboxSelected>>", on_king_combo_change)
        
        row_idx += 1
        
        # Player stats
        #  - Dice
        #  - Health
        #  - Explode pool
        #  - Guaranteed hits
        #  - Guaranteed defends
        tk.Label(self, text="Your Dice").grid(row=row_idx, column=0, sticky=tk.E)
        self.p_dice_var = tk.IntVar(value=3)
        tk.Entry(self, textvariable=self.p_dice_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Your Health").grid(row=row_idx, column=0, sticky=tk.E)
        self.p_health_var = tk.IntVar(value=5)
        tk.Entry(self, textvariable=self.p_health_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Your Explode Pool").grid(row=row_idx, column=0, sticky=tk.E)
        self.p_explode_var = tk.IntVar(value=1)
        tk.Entry(self, textvariable=self.p_explode_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Your Guaranteed Hits").grid(row=row_idx, column=0, sticky=tk.E)
        self.p_g_hits_var = tk.IntVar(value=0)
        tk.Entry(self, textvariable=self.p_g_hits_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Your Guaranteed Defends").grid(row=row_idx, column=0, sticky=tk.E)
        self.p_g_def_var = tk.IntVar(value=0)
        tk.Entry(self, textvariable=self.p_g_def_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        # Enemy stats
        tk.Label(self, text="Enemy Dice").grid(row=row_idx, column=0, sticky=tk.E)
        self.e_dice_var = tk.IntVar(value=3)
        tk.Entry(self, textvariable=self.e_dice_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Enemy Health").grid(row=row_idx, column=0, sticky=tk.E)
        self.e_health_var = tk.IntVar(value=5)
        tk.Entry(self, textvariable=self.e_health_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Enemy Explode Pool").grid(row=row_idx, column=0, sticky=tk.E)
        self.e_explode_var = tk.IntVar(value=1)
        tk.Entry(self, textvariable=self.e_explode_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Enemy Guaranteed Hits").grid(row=row_idx, column=0, sticky=tk.E)
        self.e_g_hits_var = tk.IntVar(value=0)
        tk.Entry(self, textvariable=self.e_g_hits_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        tk.Label(self, text="Enemy Guaranteed Defends").grid(row=row_idx, column=0, sticky=tk.E)
        self.e_g_def_var = tk.IntVar(value=0)
        tk.Entry(self, textvariable=self.e_g_def_var).grid(row=row_idx, column=1)
        row_idx += 1
        
        # Results display
        self.result_var_pwin = tk.StringVar(value="0%")
        self.result_var_ewin = tk.StringVar(value="0%")
        self.result_var_both_survive = tk.StringVar(value="0%")
        self.result_var_both_die = tk.StringVar(value="0%")
        
        tk.Label(self, text="You kill Enemy, survive:").grid(row=row_idx, column=0, sticky=tk.E)
        tk.Label(self, textvariable=self.result_var_pwin).grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1
        
        tk.Label(self, text="Enemy kills you, survives:").grid(row=row_idx, column=0, sticky=tk.E)
        tk.Label(self, textvariable=self.result_var_ewin).grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1
        
        tk.Label(self, text="Both survive:").grid(row=row_idx, column=0, sticky=tk.E)
        tk.Label(self, textvariable=self.result_var_both_survive).grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1
        
        tk.Label(self, text="Both die:").grid(row=row_idx, column=0, sticky=tk.E)
        tk.Label(self, textvariable=self.result_var_both_die).grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1
        
        # Simulate Button
        simulate_button = tk.Button(self, text="Simulate", command=self.run_simulation)
        simulate_button.grid(row=row_idx, column=0, columnspan=2, pady=10)
        
    def run_simulation(self):
        iterations = self.iterations_var.get()
        p_dice = self.p_dice_var.get()
        p_health = self.p_health_var.get()
        p_explode = self.p_explode_var.get()
        p_g_hits = self.p_g_hits_var.get()
        p_g_def = self.p_g_def_var.get()
        
        e_dice = self.e_dice_var.get()
        e_health = self.e_health_var.get()
        e_explode = self.e_explode_var.get()
        e_g_hits = self.e_g_hits_var.get()
        e_g_def = self.e_g_def_var.get()
        
        is_day = (self.day_night_var.get() == "Day")
        is_king = self.king_var.get()
        
        p_win_pct, e_win_pct, both_survive_pct, both_die_pct = run_monte_carlo(
            iterations,
            p_dice, p_health, p_explode, p_g_hits, p_g_def,
            e_dice, e_health, e_explode, e_g_hits, e_g_def,
            is_day, is_king
        )
        
        # Update display
        self.result_var_pwin.set(f"{p_win_pct:.2f}%")
        self.result_var_ewin.set(f"{e_win_pct:.2f}%")
        self.result_var_both_survive.set(f"{both_survive_pct:.2f}%")
        self.result_var_both_die.set(f"{both_die_pct:.2f}%")


def main():
    app = ArmelloCombatSimulator()
    app.mainloop()

if __name__ == "__main__":
    main()
