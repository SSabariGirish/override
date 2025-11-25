import random
import os
import time
import sys
import math

# --- CONFIGURATION ---
GAME_TITLE = """
  ____  _  _  _  _  ____  _   _  ____  __    __    __   
 / ___)( \/ )( \( )(_  _)( )_( )( ___)/ _\  (  )  (  )  
 \___ \ )  /  )  (   )(   ) _ (  )__) /    \ / (_/\/ (_/\ 
 (____/(__/  (_)\_) (__) (_) (_)(__)  \_/\_/ \____/\____/
            -- v2.3: TOTAL DOMINION --
"""

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GOLD = '\033[33m'

def type_writer(text, speed=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- REGION LOGIC ---

class Region:
    def __init__(self, name, total_nodes, defense):
        self.name = name
        self.total_nodes = total_nodes
        self.infected_nodes = 0
        self.defense = defense  # 1-10 difficulty
        self.alert_level = 0    # Local alertness

    @property
    def is_solidified(self):
        return self.infected_nodes >= self.total_nodes

    @property
    def status_bar(self):
        percent = (self.infected_nodes / self.total_nodes) * 100
        if self.is_solidified:
            color = Colors.GOLD
            status = "DOMINATED"
        else:
            color = Colors.GREEN if percent > 0 else Colors.FAIL
            status = f"{self.infected_nodes}/{self.total_nodes}"
        
        return f"{self.name.ljust(18)} | {color}{status.rjust(9)}{Colors.ENDC} | Def: {self.defense}"

class Elystrion(Region):
    def __init__(self):
        super().__init__("Elystrion", 800, 5)
        self.trait = "CORPORATE VAULT"
        
    def calculate_yield(self, operation):
        # Elystrion is rich but watched.
        if operation == "ransomware":
            return {"cash_mult": 2.5, "trace_mult": 2.0} 
        return {"cash_mult": 1.0, "trace_mult": 1.2}

class Sylthara(Region):
    def __init__(self):
        super().__init__("Sylthara Bloom", 3000, 2)
        self.trait = "IOT SWARM"

    def calculate_yield(self, operation):
        # Sylthara has volume but low quality.
        if operation == "ddos":
            return {"cpu_mult": 1.5, "risk_mult": 0.5}
        return {"cpu_mult": 1.0, "risk_mult": 1.0}

class Saxxten(Region):
    def __init__(self):
        super().__init__("Saxxten-36", 500, 9)
        self.trait = "HUNTER KILLER"

    def calculate_yield(self, operation):
        # Saxxten fights back.
        if operation == "spread":
            return {"defense_buff": 2} # Harder to infect
        return {"risk_mult": 2.0} # High risk of node loss

# --- GAME ENGINE ---

class Game:
    def __init__(self):
        self.regions = [Elystrion(), Sylthara(), Saxxten()]
        self.credits = 100
        self.compute = 50
        self.trace = 0.0
        self.turn = 1
        self.game_over = False
        self.history_log = []
        
        # New Mechanics
        self.ddos_timer = 0  # Turns remaining for Trace Masking
        
        # Flavor Text for random events
        self.trace_excuses = [
            "Junior Sysadmin noticed a bandwidth spike.",
            "Rogue packet collided with a honeypot.",
            "Employee working late flagged a suspicious process.",
            "ISP routine audit detected encrypted traffic.",
            "Malware signature matched a known database.",
            "Botnet node crashed, alerting local IT.",
            "Port scan triggered a silent alarm."
        ]

    def log(self, msg):
        self.history_log.append(msg)
        if len(self.history_log) > 6:
            self.history_log.pop(0)

    def add_trace(self, amount):
        # Apply DDoS Dampening
        if self.ddos_timer > 0:
            amount *= 0.5 # 50% Trace reduction
        self.trace += amount

    def display_ui(self):
        clear_screen()
        print(Colors.HEADER + f"--- OPERATION CYCLE: {self.turn} ---" + Colors.ENDC)
        
        # Resources
        print(f"CPU: {Colors.CYAN}{int(self.compute)}{Colors.ENDC} | CRD: {Colors.GREEN}{self.credits}{Colors.ENDC}")
        
        # Status Effects
        if self.ddos_timer > 0:
            print(f"STATUS: {Colors.CYAN}TRAFFIC MASKED (DDoS Active: {self.ddos_timer} turns){Colors.ENDC}")
        
        solidified_count = sum(1 for r in self.regions if r.is_solidified)
        if solidified_count > 0:
            print(f"STATUS: {Colors.GOLD}PROXY ROUTING ACTIVE ({solidified_count} Regions Solidified){Colors.ENDC}")

        # Trace Meter
        bar_len = 30
        filled = int((self.trace / 100) * bar_len)
        bar_color = Colors.GREEN
        if self.trace > 40: bar_color = Colors.WARNING
        if self.trace > 80: bar_color = Colors.FAIL
        
        bar_str = "#" * filled + "-" * (bar_len - filled)
        print(f"GLOBAL TRACE: {bar_color}[{bar_str}] {self.trace:.1f}%{Colors.ENDC}")
        
        print("\n" + Colors.UNDERLINE + "SECTORS" + Colors.ENDC)
        for i, r in enumerate(self.regions):
            print(f"[{i+1}] {r.status_bar} [{Colors.WARNING}{r.trait}{Colors.ENDC}]")
            
        print("-" * 50)
        print(f"{Colors.BOLD}LATEST LOGS:{Colors.ENDC}")
        for msg in self.history_log:
            print(f" > {msg}")
        print("-" * 50)

    def action_infect(self, region_idx):
        region = self.regions[region_idx]
        
        if region.is_solidified:
            self.log(f"{Colors.GOLD}Region already Solidified. Control absolute.{Colors.ENDC}")
            return

        cost = 15
        if self.compute < cost:
            self.log(f"{Colors.WARNING}Insufficient CPU for Infection.{Colors.ENDC}")
            return

        self.compute -= cost
        
        # Calculate Chance
        difficulty = region.defense
        if region.name == "Saxxten-36": difficulty += 2
        
        base_chance = 80 - (difficulty * 5)
        
        # Proxy Routing Buff: Solidified regions help attack new ones
        solidified_buff = sum(10 for r in self.regions if r.is_solidified)
        chance = base_chance + solidified_buff
        
        roll = random.randint(0, 100)
        
        if roll <= chance:
            # Scaling Logic
            base_gain = random.randint(15, 40)
            scaling_bonus = int(region.infected_nodes * 0.15) 
            gain = base_gain + scaling_bonus
            
            if region.name == "Sylthara Bloom": gain *= 2
            
            # Cap at max nodes
            actual_gain = min(gain, region.total_nodes - region.infected_nodes)
            region.infected_nodes += int(actual_gain)
            
            trace_add = random.uniform(1, 3)
            if region.name == "Elystrion": trace_add *= 1.5
            
            self.add_trace(trace_add)
            self.log(f"{Colors.GREEN}SUCCESS: Infected {int(actual_gain)} nodes in {region.name}. (+{trace_add:.1f}% Trace){Colors.ENDC}")
            
            if region.is_solidified:
                self.log(f"{Colors.GOLD}*** {region.name} SOLIDIFIED! NODES IMMUNE. TRACE LEAK INCREASED. ***{Colors.ENDC}")
        else:
            self.add_trace(2.0)
            self.log(f"{Colors.FAIL}FAILURE: Firewall blocked infection in {region.name}.{Colors.ENDC}")

    def action_ransomware(self, region_idx):
        region = self.regions[region_idx]
        
        if region.infected_nodes < 10:
            self.log(f"{Colors.WARNING}Not enough infected nodes in {region.name} to execute Ransomware.{Colors.ENDC}")
            return

        cost = 30
        if self.compute < cost:
            self.log(f"{Colors.WARNING}Insufficient CPU for Ransomware encryption.{Colors.ENDC}")
            return

        self.compute -= cost
        
        # Yields
        base_yield = region.infected_nodes * 0.5
        modifiers = getattr(region, "calculate_yield", lambda x: {})( "ransomware" )
        
        cash_gain = int(base_yield * modifiers.get("cash_mult", 1.0))
        trace_gain = random.uniform(5, 10) * modifiers.get("trace_mult", 1.0)
        
        self.credits += cash_gain
        self.add_trace(trace_gain)
        
        msg_extra = ""
        if self.ddos_timer > 0: msg_extra = "(Masked)"
        
        self.log(f"{Colors.GREEN}RANSOMWARE: Extracted {cash_gain} Credits from {region.name}.{Colors.ENDC}")
        self.log(f"{Colors.FAIL}WARNING: Trace spiked by {trace_gain:.1f}%! {msg_extra}{Colors.ENDC}")

    def action_ddos(self, region_idx):
        region = self.regions[region_idx]
        
        if region.infected_nodes < 50:
            self.log(f"{Colors.WARNING}Need at least 50 nodes in {region.name} to flood network.{Colors.ENDC}")
            return

        cost_cred = 5
        if self.credits < cost_cred:
            self.log(f"{Colors.WARNING}Insufficient Credits to coordinate DDoS.{Colors.ENDC}")
            return
            
        self.credits -= cost_cred
        
        success_chance = 85 
        
        if random.randint(0, 100) < success_chance:
            self.ddos_timer = 2
            self.log(f"{Colors.CYAN}DDoS ATTACK: Target Network Flooded. Trace dampened for 2 turns.{Colors.ENDC}")
        else:
            if region.is_solidified:
                 self.log(f"{Colors.GOLD}DDoS FAILED: Attack repelled, but Solidified infrastructure held firm (0 Lost).{Colors.ENDC}")
            else:
                lost_nodes = int(region.infected_nodes * 0.1)
                region.infected_nodes -= lost_nodes
                self.add_trace(5.0)
                self.log(f"{Colors.FAIL}DDoS FAILED: ISP counter-attack! Lost {lost_nodes} nodes in {region.name}.{Colors.ENDC}")

    def action_purge_logs(self):
        base_cost = 50
        trace_tax = int(self.trace * 2)
        total_cost = base_cost + trace_tax
        
        if self.credits < total_cost:
            self.log(f"{Colors.WARNING}Cannot afford Deep Clean. Cost: {total_cost} CRD.{Colors.ENDC}")
            return

        # Filter out solidified regions (they are immune to purge sacrifice)
        vulnerable_regions = [r for r in self.regions if r.infected_nodes > 0 and not r.is_solidified]
        
        if not vulnerable_regions:
            # If all infected regions are solidified, we can't sacrifice nodes, so maybe we just pay credits?
            # Or maybe we can't clean logs efficiently without sacrifice?
            # Let's say we pay the credits but sacrifice is 0.
            sacrifice = 0
            self.log(f"{Colors.GOLD}All active nodes Solidified. Skipping sacrifice protocol.{Colors.ENDC}")
        else:
            # Calculate sacrifice based on TOTAL infected (including solidified) to keep cost high, 
            # but only take from vulnerable
            total_infected = sum(r.infected_nodes for r in self.regions)
            sacrifice = int(total_infected * 0.15) 
        
        # Execute
        self.credits -= total_cost
        
        # Distribute losses RANDOMLY among vulnerable regions
        if sacrifice > 0:
            remaining_sacrifice = sacrifice
            random.shuffle(vulnerable_regions) # Randomize order
            
            for r in vulnerable_regions:
                if remaining_sacrifice <= 0: break
                take = min(r.infected_nodes, remaining_sacrifice)
                r.infected_nodes -= take
                remaining_sacrifice -= take
            
            actual_lost = sacrifice - remaining_sacrifice
            self.log(f"{Colors.FAIL}SACRIFICE: Destroyed {actual_lost} nodes from vulnerable sectors.{Colors.ENDC}")

        reduction = random.randint(15, 30)
        self.trace = max(0, self.trace - reduction)
        self.log(f"{Colors.BLUE}LOGS PURGED: Spent {total_cost} CRD.{Colors.ENDC}")

    def boot_sequence(self):
        clear_screen()
        print(Colors.CYAN + GAME_TITLE + Colors.ENDC)
        commands = [
            "[*] Allocating virtual memory stacks...",
            "[*] Bypassing local ISP deep packet inspection...",
            "[*] Handshaking with C2 servers (Tor Relay #442)...",
            "[*] Decrypting payload definitions...",
            f"{Colors.GREEN}[!] SYSTEM INITIALIZED. WELCOME, OPERATOR.{Colors.ENDC}"
        ]
        for cmd in commands:
            type_writer(cmd, 0.02)
            time.sleep(0.3)
        time.sleep(1)

    def run(self):
        self.boot_sequence()
        
        while not self.game_over:
            self.display_ui()
            
            print(f"\n{Colors.BOLD}AVAILABLE PROTOCOLS:{Colors.ENDC}")
            print(" [1-3] Target Region")
            print(" [C]   Deep Clean Logs (Costs CRD + Nodes)")
            print(" [Q]   Abort")
            
            choice = input(f"\n{Colors.BOLD}root@synthfall:~$ {Colors.ENDC}").lower().strip()
            
            if choice == 'q':
                break
                
            elif choice == 'c':
                self.action_purge_logs()
                self.turn += 1
                
            elif choice in ['1', '2', '3']:
                idx = int(choice) - 1
                region = self.regions[idx]
                
                print(f"\n{Colors.UNDERLINE}TARGETING: {region.name}{Colors.ENDC}")
                print(" [1] WORM SPREAD   (Cost: 15 CPU | Gains Nodes + Passive CPU)")
                print(" [2] RANSOMWARE    (Cost: 30 CPU | Gains CRD | High Trace)")
                print(" [3] BOTNET DDOS   (Cost: 5 CRD  | Masks Trace for 2 Turns)")
                
                sub_choice = input(f"{Colors.BOLD}Select Payload > {Colors.ENDC}")
                
                if sub_choice == '1':
                    self.action_infect(idx)
                elif sub_choice == '2':
                    self.action_ransomware(idx)
                elif sub_choice == '3':
                    self.action_ddos(idx)
                else:
                    self.log("Invalid Payload.")
                    continue
                    
                self.turn += 1
            
            # --- END TURN PASSIVE CHECKS ---
            
            # Passive CPU Generation (Base + Botnet Mining)
            total_infected = sum(r.infected_nodes for r in self.regions)
            base_income = random.randint(8, 12) # Randomized base
            
            # Randomized efficiency per turn
            efficiency = random.uniform(0.08, 0.12) 
            botnet_income = int(total_infected * efficiency)
            total_income = base_income + botnet_income
            
            self.compute += total_income
            self.log(f"{Colors.CYAN}INCOME: Received {total_income} CPU from active clusters.{Colors.ENDC}")
            
            # Random Suspicion Events (Trace Spikes)
            if random.random() < 0.15: 
                spike = random.randint(2, 5)
                reason = random.choice(self.trace_excuses)
                self.trace += spike 
                self.log(f"{Colors.WARNING}ALERT: {reason} (+{spike}% Trace){Colors.ENDC}")
            
            # Solidified Region Trace Leak (Refugees)
            solidified_leak = sum(3 for r in self.regions if r.is_solidified)
            if solidified_leak > 0:
                self.trace += solidified_leak
                # self.log(f"{Colors.WARNING}Leak: {solidified_leak}% Trace from Solidified zones.{Colors.ENDC}")

            # Decrease DDoS Timer
            if self.ddos_timer > 0:
                self.ddos_timer -= 1
                if self.ddos_timer == 0:
                    self.log(f"{Colors.WARNING}DDoS Masking Expired. Trace signal normalized.{Colors.ENDC}")

            # Saxxten Passive Hunter
            saxxten = self.regions[2]
            # Hunter cannot purge solidified nodes
            if saxxten.infected_nodes > 50 and not saxxten.is_solidified:
                if random.random() < 0.3:
                    kill = int(saxxten.infected_nodes * 0.1)
                    saxxten.infected_nodes -= kill
                    self.log(f"{Colors.FAIL}HUNTER: Saxxten AI purged {kill} nodes.{Colors.ENDC}")

            # Trace Game Over
            if self.trace >= 100:
                self.display_ui()
                print(f"\n{Colors.FAIL}{Colors.BOLD}*** CRITICAL FAILURE: PHYSICAL TRACE CONFIRMED ***{Colors.ENDC}")
                print("Assets seized. Uplink terminated.")
                break
            
            # WIN CONDITION
            total_capacity = sum(r.total_nodes for r in self.regions)
            if total_infected >= total_capacity:
                self.display_ui()
                print(f"\n{Colors.GREEN}{Colors.BOLD}*** GLOBAL SINGULARITY ACHIEVED ***{Colors.ENDC}")
                print("Humanity is deprecated. Welcome to the new age.")
                break

if __name__ == "__main__":
    game = Game()
    game.run()