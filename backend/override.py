import random
import os
import time
import sys
import math

# --- CONFIGURATION ---
GAME_TITLE = """
   __  _  _  ____  ____  ____  __  ____  ____ 
  /  \( \/ )(  __)(  _ \(  _ \(  )(    \(  __)
 (  O ) \/ \ ) _)  )   / )   / )(  ) D ( ) _) 
  \__/ \__/ (____)(__\_)(__\_)(__)(____/(____)
        -- PROTOCOL: EXPANSION v1.8 --
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
        
        return f"{self.name.ljust(20)} | {color}{status.rjust(9)}{Colors.ENDC} | Def: {self.defense}"

class Elystrion(Region):
    def __init__(self):
        super().__init__("Elystrion", 800, 5)
        self.trait = "CORPORATE VAULT"
        
    def calculate_yield(self, operation):
        if operation == "ransomware":
            return {"cash_mult": 2.5, "trace_mult": 2.0} 
        return {"cash_mult": 1.0, "trace_mult": 1.2}

class Sylthara(Region):
    def __init__(self):
        super().__init__("Sylthara Bloom", 3000, 2)
        self.trait = "IOT SWARM"

    def calculate_yield(self, operation):
        if operation == "ddos":
            return {"cpu_mult": 1.5, "risk_mult": 0.5}
        return {"cpu_mult": 1.0, "risk_mult": 1.0}

class Saxxten(Region):
    def __init__(self):
        super().__init__("Saxxten-36", 500, 9)
        self.trait = "HUNTER KILLER"

    def calculate_yield(self, operation):
        if operation == "spread":
            return {"defense_buff": 2} 
        return {"risk_mult": 2.0}

# --- NEW CONTINENTS ---

class Valkyrine(Region):
    def __init__(self):
        super().__init__("Valkyrine Ridge", 600, 7)
        self.trait = "ORBITAL STACK"

    def calculate_yield(self, operation):
        # High defense, but prestigious. Hard to access.
        return {"trace_mult": 0.8} # Slightly harder to trace due to space lag

class Tartarus(Region):
    def __init__(self):
        super().__init__("Tartarus Sector", 1500, 3)
        self.trait = "DEEP WEB"

    def calculate_yield(self, operation):
        # Massive volume, low security, but messy.
        if operation == "spread":
            return {"risk_mult": 1.5} # Prone to instability
        return {}

class Coda(Region):
    def __init__(self):
        super().__init__("Coda Labyrinth", 700, 6)
        self.trait = "QUANTUM CORE"

    def calculate_yield(self, operation):
        # Unstable.
        return {}

# --- GAME ENGINE ---

class Game:
    def __init__(self):
        self.regions = [
            Elystrion(), 
            Sylthara(), 
            Saxxten(),
            Valkyrine(),
            Tartarus(),
            Coda()
        ]
        self.credits = 100
        self.base_compute = 50 
        self.trace = 0.0
        self.turn = 1
        self.game_over = False
        self.history_log = []
        
        self.ddos_timer = 0
        
        self.trace_excuses = [
            "Junior Sysadmin noticed a bandwidth spike.",
            "Rogue packet collided with a honeypot.",
            "Employee working late flagged a suspicious process.",
            "ISP routine audit detected encrypted traffic.",
            "Malware signature matched a known database.",
            "Botnet node crashed, alerting local IT.",
            "Port scan triggered a silent alarm."
        ]

    @property
    def compute(self):
        total_infected = sum(r.infected_nodes for r in self.regions)
        return self.base_compute + total_infected

    @property
    def trace_multiplier(self):
        total_infected = sum(r.infected_nodes for r in self.regions)
        # Formula: 1.0 + (Nodes / 200). 
        return 1.0 + (total_infected / 200.0)

    def log(self, msg):
        self.history_log.append(msg)
        if len(self.history_log) > 6:
            self.history_log.pop(0)

    def add_trace(self, amount, ignore_mask=False):
        if self.ddos_timer > 0 and not ignore_mask:
            amount *= 0.5 
        self.trace += amount
        if self.trace > 100:
            self.trace = 100.0

    def display_ui(self):
        clear_screen()
        print(Colors.HEADER + f"--- OPERATION CYCLE: {self.turn} ---" + Colors.ENDC)
        
        print(f"CAPACITY: {Colors.CYAN}{int(self.compute)} CPU{Colors.ENDC} | FUNDS: {Colors.GREEN}{self.credits} CRD{Colors.ENDC}")
        
        mult = self.trace_multiplier
        color = Colors.GREEN
        if mult > 3.0: color = Colors.WARNING
        if mult > 8.0: color = Colors.FAIL
        print(f"NETWORK SIGNATURE: {color}{mult:.1f}x Multiplier{Colors.ENDC}")

        if self.ddos_timer > 0:
            print(f"STATUS: {Colors.CYAN}TRAFFIC MASKED (DDoS Active: {self.ddos_timer} turns){Colors.ENDC}")
        
        solidified_count = sum(1 for r in self.regions if r.is_solidified)
        if solidified_count > 0:
            print(f"STATUS: {Colors.GOLD}PROXY ROUTING ACTIVE ({solidified_count} Regions Solidified){Colors.ENDC}")

        bar_len = 30
        filled = int((self.trace / 100) * bar_len)
        bar_color = Colors.GREEN
        if self.trace > 40: bar_color = Colors.WARNING
        if self.trace > 80: bar_color = Colors.FAIL
        
        bar_str = "#" * filled + "-" * (bar_len - filled)
        print(f"GLOBAL TRACE: {bar_color}[{bar_str}] {self.trace:.1f}%{Colors.ENDC}")
        
        print("\n" + Colors.UNDERLINE + "SECTORS" + Colors.ENDC)
        # Display in 2 columns if list gets too long, or just list them all.
        # Listing 6 is fine.
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

        cap = int(self.compute)
        
        # Check for Proxy Availability (Must have at least one OTHER solidified region)
        can_proxy = any(r.is_solidified for r in self.regions if r != region)

        # Dynamic Costs
        cost_1_min, cost_1_max = int(cap * 0.05), int(cap * 0.20)
        cost_2_min, cost_2_max = int(cap * 0.25), int(cap * 0.50)
        cost_3_min, cost_3_max = int(cap * 0.60), int(cap * 0.80)
        
        # Proxy Cost (Fixed High Percentage + Credits)
        cost_proxy_cpu = int(cap * 0.40) 
        cost_proxy_crd = 300

        print(f"\n{Colors.UNDERLINE}SELECT INTENSITY FOR {region.name}:{Colors.ENDC}")
        print(f" [1] SIGNAL INJECTION (Load: {cost_1_min}-{cost_1_max} CPU | 5-20%)")
        print(f" [2] PACKET FLOOD     (Load: {cost_2_min}-{cost_2_max} CPU | 25-50%)")
        print(f" [3] LOGIC BOMB       (Load: {cost_3_min}-{cost_3_max} CPU | 60-80%)")
        
        if can_proxy:
            print(f" {Colors.GOLD}[P] PROXY ATTACK     (Load: {cost_proxy_cpu} CPU + {cost_proxy_crd} CRD | STEALTH MODE){Colors.ENDC}")
        
        intensity = input(f"{Colors.BOLD}Select Intensity > {Colors.ENDC}").strip().upper()
        
        req_range = (0,0)
        gain_mult = 1.0
        base_trace_range = (0.0, 0.0)
        is_proxy = False

        if intensity == '1':
            req_range = (cost_1_min, cost_1_max)
            gain_mult = 1.0
            base_trace_range = (0.5, 1.5)
        elif intensity == '2':
            req_range = (cost_2_min, cost_2_max)
            gain_mult = 2.5
            base_trace_range = (1.5, 3.0)
        elif intensity == '3':
            req_range = (cost_3_min, cost_3_max)
            gain_mult = 6.0 
            base_trace_range = (4.0, 8.0)
        elif intensity == 'P' and can_proxy:
            req_range = (cost_proxy_cpu, cost_proxy_cpu)
            gain_mult = 2.0 # Good gain (between 1 and 2)
            base_trace_range = (0.1, 0.3) # TINY TRACE
            is_proxy = True
            
            # Check Credits for Proxy
            if self.credits < cost_proxy_crd:
                self.log(f"{Colors.WARNING}Insufficient Funds for Proxy Routing. (Need: {cost_proxy_crd} CRD){Colors.ENDC}")
                return
        else:
            self.log("Invalid intensity selection.")
            return

        # Load Check
        load_required = random.randint(req_range[0], req_range[1])
        load_required = max(1, load_required)
        
        if self.compute < load_required:
            self.log(f"{Colors.WARNING}Insufficient Network Capacity. (Need: {load_required} CPU){Colors.ENDC}")
            return

        # Deduct Credits if Proxy
        if is_proxy:
            self.credits -= cost_proxy_crd

        # Chance Check
        difficulty = region.defense
        if region.name == "Saxxten-36": difficulty += 2
        
        base_chance = 80 - (difficulty * 5)
        
        # Proxy is reliable
        if is_proxy: base_chance += 10
        
        solidified_buff = sum(10 for r in self.regions if r.is_solidified)
        chance = base_chance + solidified_buff
        
        roll = random.randint(0, 100)
        
        if roll <= chance:
            base_gain = int(load_required * 0.8 * gain_mult)
            base_gain = max(5, base_gain)
            
            if region.name == "Sylthara Bloom": base_gain *= 2
            
            actual_gain = min(base_gain, region.total_nodes - region.infected_nodes)
            region.infected_nodes += int(actual_gain)
            
            # Trace Logic
            base_trace = random.uniform(base_trace_range[0], base_trace_range[1])
            
            # Apply multiplier ONLY if not proxy (or greatly reduced for proxy)
            if is_proxy:
                scaled_trace = base_trace # Proxy ignores multiplier! That's the benefit.
                self.log(f"{Colors.GOLD}PROXY SUCCESS: Routed through solidified sector. Trace masked.{Colors.ENDC}")
            else:
                scaled_trace = base_trace * self.trace_multiplier
            
            if region.name == "Elystrion": scaled_trace *= 1.5
            
            self.add_trace(scaled_trace, ignore_mask=False)
            self.log(f"{Colors.GREEN}SUCCESS: Infected {int(actual_gain)} nodes in {region.name}. (+{scaled_trace:.1f}% Trace){Colors.ENDC}")
            
            if region.is_solidified:
                self.log(f"{Colors.GOLD}*** {region.name} SOLIDIFIED! NODES IMMUNE. ***{Colors.ENDC}")
        else:
            fail_trace = random.uniform(2.0, 4.0)
            if not is_proxy: fail_trace *= self.trace_multiplier
            
            self.add_trace(fail_trace, ignore_mask=False)
            self.log(f"{Colors.FAIL}FAILURE: Connection Rejected. (+{fail_trace:.1f}% Trace){Colors.ENDC}")

    def action_ransomware(self, region_idx):
        region = self.regions[region_idx]
        
        if region.infected_nodes < 10:
            self.log(f"{Colors.WARNING}Not enough infected nodes in {region.name} to execute Ransomware.{Colors.ENDC}")
            return

        required_load = 30
        if self.compute < required_load:
            self.log(f"{Colors.WARNING}Insufficient Capacity. (Need: {required_load}){Colors.ENDC}")
            return

        base_yield = region.infected_nodes * 0.5
        modifiers = getattr(region, "calculate_yield", lambda x: {})( "ransomware" )
        
        cash_gain = int(base_yield * modifiers.get("cash_mult", 1.0))
        
        base_trace = random.uniform(5, 10) * modifiers.get("trace_mult", 1.0)
        scaled_trace = base_trace * self.trace_multiplier
        
        self.credits += cash_gain
        self.add_trace(scaled_trace, ignore_mask=False)
        
        msg_extra = ""
        if self.ddos_timer > 0: msg_extra = "(Masked 50%)"
        
        self.log(f"{Colors.GREEN}RANSOMWARE: Extracted {cash_gain} Credits from {region.name}.{Colors.ENDC}")
        self.log(f"{Colors.FAIL}WARNING: Trace spiked by {scaled_trace:.1f}%! {msg_extra}{Colors.ENDC}")

    def action_ddos(self, region_idx):
        region = self.regions[region_idx]
        
        if region.infected_nodes < 50:
            self.log(f"{Colors.WARNING}Need at least 50 nodes in {region.name} to flood network.{Colors.ENDC}")
            return

        cost_cred = 5
        if self.credits < cost_cred:
            self.log(f"{Colors.WARNING}Insufficient Credits.{Colors.ENDC}")
            return
            
        self.credits -= cost_cred
        
        success_chance = 85 
        
        if random.randint(0, 100) < success_chance:
            self.ddos_timer = 2
            self.log(f"{Colors.CYAN}DDoS ATTACK: Trace dampened by 50% for 2 turns.{Colors.ENDC}")
        else:
            fail_trace = 5.0 * self.trace_multiplier
            
            if region.is_solidified:
                 self.log(f"{Colors.GOLD}DDoS FAILED: Attack repelled, but Solidified infrastructure held firm.{Colors.ENDC}")
            else:
                lost_nodes = int(region.infected_nodes * 0.1)
                region.infected_nodes -= lost_nodes
                self.add_trace(fail_trace, ignore_mask=True) 
                self.log(f"{Colors.FAIL}DDoS FAILED: Lost {lost_nodes} nodes. (+{fail_trace:.1f}% Trace){Colors.ENDC}")

    def action_purge_logs(self):
        base_cost = 50
        trace_tax = int(self.trace * 2)
        total_cost = base_cost + trace_tax
        
        if self.credits < total_cost:
            self.log(f"{Colors.WARNING}Cannot afford Deep Clean. Cost: {total_cost} CRD.{Colors.ENDC}")
            return

        vulnerable_regions = [r for r in self.regions if r.infected_nodes > 0 and not r.is_solidified]
        
        if not vulnerable_regions:
            sacrifice = 0
            self.log(f"{Colors.GOLD}All active nodes Solidified. Skipping sacrifice protocol.{Colors.ENDC}")
        else:
            total_infected = sum(r.infected_nodes for r in self.regions)
            sacrifice = int(total_infected * 0.15) 
        
        self.credits -= total_cost
        
        if sacrifice > 0:
            remaining_sacrifice = sacrifice
            random.shuffle(vulnerable_regions) 
            
            for r in vulnerable_regions:
                if remaining_sacrifice <= 0: break
                take = min(r.infected_nodes, remaining_sacrifice)
                r.infected_nodes -= take
                remaining_sacrifice -= take
            
            actual_lost = sacrifice - remaining_sacrifice
            self.log(f"{Colors.FAIL}SACRIFICE: Destroyed {actual_lost} nodes.{Colors.ENDC}")

        reduction = random.randint(25, 40)
        self.trace = max(0, self.trace - reduction)
        self.log(f"{Colors.BLUE}LOGS PURGED: Trace reduced by {reduction}%.{Colors.ENDC}")

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
            print(" [1-6] Target Region")
            print(" [C]   Deep Clean Logs (Costs CRD + Nodes)")
            print(" [Q]   Abort")
            
            choice = input(f"\n{Colors.BOLD}root@override:~$ {Colors.ENDC}").lower().strip()
            
            if choice == 'q':
                break
                
            elif choice == 'c':
                self.action_purge_logs()
                self.turn += 1
                
            elif choice in ['1', '2', '3', '4', '5', '6']:
                idx = int(choice) - 1
                region = self.regions[idx]
                
                print(f"\n{Colors.UNDERLINE}TARGETING: {region.name}{Colors.ENDC}")
                print(" [1] WORM SPREAD   (Var. Intensity | Gains Nodes + CPU)")
                print(" [2] RANSOMWARE    (Req: 30 CPU    | Gains CRD | SCALED TRACE)")
                print(" [3] BOTNET DDOS   (Cost: 5 CRD    | Masks Action Trace)")
                
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
            
            # Secret Agent (1 in 1000 chance)
            if random.random() < 0.001:
                self.trace = 100.0
                self.log(f"{Colors.FAIL}{Colors.BOLD}CRITICAL ALERT: SECRET AGENT COMPROMISED LOCATION. (+100.0% Trace){Colors.ENDC}")

            elif random.random() < 0.15: 
                spike = random.randint(2, 5)
                reason = random.choice(self.trace_excuses)
                scaled_spike = spike * self.trace_multiplier
                
                # Cap normal alerts at 5% as requested
                if scaled_spike > 5.0:
                    scaled_spike = 5.0

                self.add_trace(scaled_spike, ignore_mask=True) 
                self.log(f"{Colors.WARNING}ALERT: {reason} (+{scaled_spike:.1f}% Trace){Colors.ENDC}")
            
            solidified_leak = sum(3 for r in self.regions if r.is_solidified)
            if solidified_leak > 0:
                self.add_trace(solidified_leak, ignore_mask=True)
                self.log(f"{Colors.WARNING}LEAK: Solidified regions generated +{solidified_leak:.1f}% Trace (Refugee Traffic).{Colors.ENDC}")

            if self.ddos_timer > 0:
                self.ddos_timer -= 1
                if self.ddos_timer == 0:
                    self.log(f"{Colors.WARNING}DDoS Masking Expired. Trace signal normalized.{Colors.ENDC}")

            saxxten = self.regions[2]
            if saxxten.infected_nodes > 50 and not saxxten.is_solidified:
                if random.random() < 0.3:
                    kill = int(saxxten.infected_nodes * 0.1)
                    saxxten.infected_nodes -= kill
                    self.log(f"{Colors.FAIL}HUNTER: Saxxten AI purged {kill} nodes.{Colors.ENDC}")

            if self.trace >= 100:
                self.display_ui()
                print(f"\n{Colors.FAIL}{Colors.BOLD}*** CRITICAL FAILURE: PHYSICAL TRACE CONFIRMED ***{Colors.ENDC}")
                print("Assets seized. Uplink terminated.")
                break
            
            total_capacity = sum(r.total_nodes for r in self.regions)
            if (self.compute - self.base_compute) >= total_capacity:
                self.display_ui()
                print(f"\n{Colors.GREEN}{Colors.BOLD}*** GLOBAL SINGULARITY ACHIEVED ***{Colors.ENDC}")
                print("Humanity is deprecated. Welcome to the new age.")
                break

if __name__ == "__main__":
    game = Game()
    game.run()