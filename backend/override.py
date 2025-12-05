import random
import os
import time
import sys
import math
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

# --- CONFIGURATION ---
GAME_VERSION = "v2.7 (Proxy Balance Update)"
SAVE_FILE = "override_save.json"

GAME_TITLE = """
   __  _  _  ____  ____  ____  __  ____  ____ 
  /  \( \/ )(  __)(  _ \(  _ \(  )(    \(  __)
 (  O ) \/ \ ) _)  )   / )   / )(  ) D ( ) _) 
  \__/ \__/ (____)(__\_)(__\_)(__)(____/(____)
        -- PROTOCOL: EXPANSION v2.7 --
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

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ----------------------------
# TRAIT SYSTEM
# ----------------------------

class Trait:
    name = "GENERIC"
    def on_infect_gain_multiplier(self) -> float: return 1.0
    def on_infect_trace_modifier(self, trace: float) -> float: return trace
    def on_ransom_multiplier(self) -> float: return 1.0
    def on_ransom_trace_modifier(self, trace: float) -> float: return trace
    def on_difficulty_modifier(self) -> int: return 0
    def on_risk_multiplier(self) -> float: return 1.0

class ElystrionTrait(Trait):
    name = "CORPORATE VAULT"
    def on_ransom_multiplier(self): return 2.5
    def on_ransom_trace_modifier(self, trace): return trace * 2.0
    def on_infect_trace_modifier(self, trace): return trace * 1.5

class SyltharaTrait(Trait):
    name = "IOT SWARM"
    def on_infect_gain_multiplier(self): return 2.0 # Base gain * 2

class SaxxtenTrait(Trait):
    name = "HUNTER KILLER"
    def on_difficulty_modifier(self): return 2
    def on_risk_multiplier(self): return 2.0

class ValkyrineTrait(Trait):
    name = "ORBITAL STACK"
    def on_infect_trace_modifier(self, trace): return trace * 0.8

class TartarusTrait(Trait):
    name = "DEEP WEB"
    def on_risk_multiplier(self): return 1.5

class CodaTrait(Trait):
    name = "QUANTUM CORE"

# ----------------------------
# DATA STRUCTURES
# ----------------------------

@dataclass
class Region:
    name: str
    total_nodes: int
    defense: int
    infected_nodes: int = 0
    ransom_count: int = 0  # Track number of ransomware attacks
    trait: Trait = field(default_factory=Trait)

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
        return f"{self.name.ljust(20)} | {color}{status.rjust(9)}{Colors.ENDC} | Def: {self.defense} | {self.trait.name}"

@dataclass
class ActionResult:
    success: bool
    events: List[str] = field(default_factory=list)

# ----------------------------
# GAME ENGINE
# ----------------------------

class GameEngine:
    def __init__(self):
        self.regions = [
            Region("Elystrion", 800, 5, trait=ElystrionTrait()),
            Region("Sylthara Bloom", 3000, 2, trait=SyltharaTrait()),
            Region("Saxxten-36", 500, 9, trait=SaxxtenTrait()),
            Region("Valkyrine Ridge", 600, 7, trait=ValkyrineTrait()),
            Region("Tartarus Sector", 1500, 3, trait=TartarusTrait()),
            Region("Coda Labyrinth", 700, 6, trait=CodaTrait())
        ]
        
        # State variables (v1.11 Defaults)
        self.credits = 100
        self.base_compute = 50
        self.trace = 0.0
        self.turn = 1
        self.game_over = False
        self.ddos_timer = 0
        self.ddos_effectiveness = 0.0
        
        self.history_log = []
        self._max_history = 8

        self.trace_excuses = [
            "Junior Sysadmin noticed a bandwidth spike.",
            "Rogue packet collided with a honeypot.",
            "Employee working late flagged a suspicious process.",
            "ISP routine audit detected encrypted traffic.",
            "Malware signature matched a known database.",
            "Botnet node crashed, alerting local IT.",
            "Port scan triggered a silent alarm."
        ]

    # --- Properties ---
    @property
    def compute(self):
        total_infected = sum(r.infected_nodes for r in self.regions)
        return self.base_compute + total_infected

    @property
    def trace_multiplier(self):
        total_infected = sum(r.infected_nodes for r in self.regions)
        # Cap at 10.0x so late game is playable but hard
        raw_mult = 1.0 + (total_infected / 200.0)
        return min(raw_mult, 10.0)

    # --- Core Logic Helpers ---
    def log(self, msg):
        self.history_log.append(msg)
        if len(self.history_log) > self._max_history:
            self.history_log.pop(0)

    def add_trace(self, amount, ignore_mask=False) -> float:
        """Adds trace and returns the actual amount added (after caps/masks)."""
        
        # DDoS Masking Logic: Multiply by (1 - effectiveness)
        # e.g., if effectiveness is 0.75 (75%), we multiply by 0.25
        if self.ddos_timer > 0 and not ignore_mask:
            amount *= (1.0 - self.ddos_effectiveness)
        
        # Safety Valve: Cap single spike at 50%
        if amount > 50.0: 
            amount = 50.0
            
        self.trace += amount
        
        # Hard Cap: 100%
        if self.trace > 100:
            self.trace = 100.0
            
        return amount

    def get_infect_costs(self):
        cap = int(self.compute)
        return {
            "1": (int(cap * 0.05), int(cap * 0.20)),
            "2": (int(cap * 0.25), int(cap * 0.50)),
            "3": (int(cap * 0.60), int(cap * 0.80)),
            "P": int(cap * 0.40)
        }

    # --- Persistence ---
    def save_game(self):
        data = {
            "credits": self.credits,
            "base_compute": self.base_compute,
            "trace": self.trace,
            "turn": self.turn,
            "ddos_timer": self.ddos_timer,
            "ddos_effectiveness": self.ddos_effectiveness,
            "history_log": self.history_log,
            "regions": []
        }
        for r in self.regions:
            # We serialize traits by name to reconstruct them later
            r_data = asdict(r)
            r_data['trait_name'] = r.trait.name
            del r_data['trait']
            data["regions"].append(r_data)
        
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            self.log(f"{Colors.BLUE}Game Saved to {SAVE_FILE}.{Colors.ENDC}")
            return True
        except Exception as e:
            self.log(f"{Colors.FAIL}Save Failed: {e}{Colors.ENDC}")
            return False

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            self.log(f"{Colors.FAIL}No save file found.{Colors.ENDC}")
            return False

        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            
            self.credits = data.get("credits", 100)
            self.base_compute = data.get("base_compute", 50)
            self.trace = data.get("trace", 0.0)
            self.turn = data.get("turn", 1)
            self.ddos_timer = data.get("ddos_timer", 0)
            self.ddos_effectiveness = data.get("ddos_effectiveness", 0.0)
            self.history_log = data.get("history_log", [])
            
            # Map trait names back to instances
            trait_map = {
                "CORPORATE VAULT": ElystrionTrait(),
                "IOT SWARM": SyltharaTrait(),
                "HUNTER KILLER": SaxxtenTrait(),
                "ORBITAL STACK": ValkyrineTrait(),
                "DEEP WEB": TartarusTrait(),
                "QUANTUM CORE": CodaTrait(),
                "GENERIC": Trait()
            }
            
            new_regions = []
            for r_data in data.get("regions", []):
                t_name = r_data.pop("trait_name", "GENERIC")
                t_inst = trait_map.get(t_name, Trait())
                
                # Rebuild Region object
                if 'trait' in r_data: del r_data['trait'] # safety
                reg = Region(trait=t_inst, **r_data)
                new_regions.append(reg)
            
            self.regions = new_regions
            self.log(f"{Colors.BLUE}Game Loaded from {SAVE_FILE}.{Colors.ENDC}")
            return True
        except Exception as e:
            self.log(f"{Colors.FAIL}Load Failed: {e}{Colors.ENDC}")
            return False

    # --- Actions ---

    def action_infect(self, region_idx, intensity):
        region = self.regions[region_idx]
        ar = ActionResult(success=False)

        if region.is_solidified:
            ar.events.append(f"{Colors.GOLD}Region already Solidified. Control absolute.{Colors.ENDC}")
            return ar

        can_proxy = any(r.is_solidified for r in self.regions if r != region)
        costs = self.get_infect_costs()
        
        req_range = (0,0)
        gain_mult = 1.0
        base_trace_range = (0.0, 0.0)
        is_proxy = False
        cost_proxy_crd = 2000  # Updated Cost

        if intensity == '1':
            req_range = costs["1"]
            gain_mult = 1.0
            base_trace_range = (0.5, 1.5)
        elif intensity == '2':
            req_range = costs["2"]
            gain_mult = 2.5
            base_trace_range = (1.5, 3.0)
        elif intensity == '3':
            req_range = costs["3"]
            gain_mult = 6.0 
            base_trace_range = (4.0, 8.0)
        elif intensity == 'P':
            if not can_proxy:
                ar.events.append("No Solidified region available for Proxy routing.")
                return ar
            if self.credits < cost_proxy_crd:
                ar.events.append(f"{Colors.WARNING}Insufficient Funds for Proxy (Need: {cost_proxy_crd} CRD).{Colors.ENDC}")
                return ar
            
            req_range = (costs["P"], costs["P"])
            gain_mult = 2.0 
            base_trace_range = (0.1, 0.3) 
            is_proxy = True
        else:
            ar.events.append("Invalid intensity.")
            return ar

        # Calculate Load
        load_required = random.randint(req_range[0], req_range[1])
        load_required = max(1, load_required)

        if self.compute < load_required:
            ar.events.append(f"{Colors.WARNING}Insufficient Capacity (Need: {load_required} CPU).{Colors.ENDC}")
            return ar

        # Pay Credits if Proxy
        if is_proxy:
            self.credits -= cost_proxy_crd

        # Calculate Chance
        difficulty = region.defense + region.trait.on_difficulty_modifier()
        base_chance = 80 - (difficulty * 5)
        if is_proxy: base_chance += 10
        solidified_buff = sum(10 for r in self.regions if r.is_solidified)
        chance = base_chance + solidified_buff

        if random.randint(0, 100) <= chance:
            # Success Logic
            base_gain = int(load_required * 0.8 * gain_mult)
            base_gain = max(5, base_gain)
            base_gain = int(base_gain * region.trait.on_infect_gain_multiplier())
            
            actual_gain = min(base_gain, region.total_nodes - region.infected_nodes)
            region.infected_nodes += int(actual_gain)
            
            # Trace Logic
            base_trace = random.uniform(base_trace_range[0], base_trace_range[1])
            
            if is_proxy:
                scaled_trace = base_trace
                ar.events.append(f"{Colors.GOLD}PROXY SUCCESS: Trace masked.{Colors.ENDC}")
            else:
                scaled_trace = base_trace * self.trace_multiplier
                scaled_trace = region.trait.on_infect_trace_modifier(scaled_trace)

            applied_trace = self.add_trace(scaled_trace)
            ar.events.append(f"{Colors.GREEN}SUCCESS: Infected {int(actual_gain)} nodes in {region.name}. (+{applied_trace:.1f}% Trace){Colors.ENDC}")
            ar.success = True

            if region.is_solidified:
                ar.events.append(f"{Colors.GOLD}*** {region.name} SOLIDIFIED! ***{Colors.ENDC}")
        else:
            # Failure Logic
            fail_trace = random.uniform(2.0, 4.0)
            if not is_proxy: 
                fail_trace *= self.trace_multiplier
            
            applied_trace = self.add_trace(fail_trace)
            ar.events.append(f"{Colors.FAIL}FAILURE: Connection Rejected. (+{applied_trace:.1f}% Trace){Colors.ENDC}")

        return ar

    def action_ransomware(self, region_idx, intensity):
        region = self.regions[region_idx]
        ar = ActionResult(success=False)

        if region.infected_nodes < 10:
            ar.events.append(f"{Colors.WARNING}Not enough infected nodes.{Colors.ENDC}")
            return ar

        if intensity == '1': # Low
            required_load = 10
            yield_mult = 0.2
            trace_base_range = (1.0, 3.0)
            tier_name = "DATA SIPHON"
        elif intensity == '2': # Med
            required_load = 40
            yield_mult = 0.6
            trace_base_range = (4.0, 8.0)
            tier_name = "ENCRYPTION"
        elif intensity == '3': # High
            required_load = 80
            yield_mult = 1.5
            trace_base_range = (10.0, 20.0)
            tier_name = "INFRASTRUCTURE LOCK"
        else:
            ar.events.append("Invalid Intensity")
            return ar

        if self.compute < required_load:
            ar.events.append(f"{Colors.WARNING}Insufficient Capacity (Need: {required_load}).{Colors.ENDC}")
            return ar

        base_yield = region.infected_nodes * yield_mult
        
        # Diminishing Returns for Dominated Regions
        diminish_factor = 1.0
        if region.is_solidified:
            # Drop 10% per attempt, capped at 10% min
            diminish_factor = max(0.1, 1.0 - (region.ransom_count * 0.1))
            region.ransom_count += 1
            
        final_yield_mult = region.trait.on_ransom_multiplier() * diminish_factor
        cash_gain = int(base_yield * final_yield_mult)
        
        base_trace = random.uniform(trace_base_range[0], trace_base_range[1])
        scaled_trace = base_trace * self.trace_multiplier
        scaled_trace = region.trait.on_ransom_trace_modifier(scaled_trace)
        
        self.credits += cash_gain
        applied_trace = self.add_trace(scaled_trace)
        
        msg_extra = ""
        if self.ddos_timer > 0: 
            msg_extra += f"(Masked {int(self.ddos_effectiveness * 100)}%) "
        
        if region.is_solidified and diminish_factor < 1.0:
            pct_yield = int(diminish_factor * 100)
            msg_extra += f"{Colors.WARNING}(Yield Dampened: {pct_yield}%){Colors.ENDC}"
        
        ar.events.append(f"{Colors.GREEN}{tier_name}: Extracted {cash_gain} Credits. (+{applied_trace:.1f}% Trace) {msg_extra}{Colors.ENDC}")
        ar.success = True
        return ar

    def action_ddos(self, region_idx, intensity):
        region = self.regions[region_idx]
        ar = ActionResult(success=False)

        if intensity == '1': # Simple
            cost_cred = 5
            req_nodes = 20
            mask = 0.25
            name = "SIMPLE DoS"
        elif intensity == '2': # Average
            cost_cred = 20
            req_nodes = 100
            mask = 0.50
            name = "DISTRIBUTED DoS"
        elif intensity == '3': # Botnet
            cost_cred = 50
            req_nodes = 300
            mask = 0.75
            name = "BOTNET SWARM"
        elif intensity == '4': # Global
            cost_cred = 150
            req_nodes = 500
            mask = 0.95
            name = "CROSS-CONTINENT BLACKOUT"
        else:
            ar.events.append("Invalid Intensity")
            return ar

        if region.infected_nodes < req_nodes:
            ar.events.append(f"{Colors.WARNING}Need {req_nodes} nodes in region.{Colors.ENDC}")
            return ar

        if self.credits < cost_cred:
            ar.events.append(f"{Colors.WARNING}Insufficient Credits (Need: {cost_cred}).{Colors.ENDC}")
            return ar

        self.credits -= cost_cred
        
        if random.randint(0, 100) < 85:
            self.ddos_timer = 3  # Start at 3 so it lasts 2 full turns after this one
            self.ddos_effectiveness = mask
            ar.events.append(f"{Colors.CYAN}{name}: Trace dampened by {int(mask*100)}% for 2 turns.{Colors.ENDC}")
            ar.success = True
        else:
            # Failure case - Credits lost, no trace spike
            if region.is_solidified:
                ar.events.append(f"{Colors.GOLD}DDoS FAILED: Credits lost, but solidified infrastructure prevented fallout.{Colors.ENDC}")
            else:
                lost_nodes = int(region.infected_nodes * 0.1)
                region.infected_nodes -= lost_nodes
                # Trace spike removed per user request
                ar.events.append(f"{Colors.FAIL}{name} FAILED: Lost {lost_nodes} nodes. (Credits consumed, No Trace Spike){Colors.ENDC}")
        
        return ar

    def action_purge_logs(self):
        ar = ActionResult(success=False)
        base_cost = 50
        trace_tax = int(self.trace * 2)
        total_cost = base_cost + trace_tax

        if self.credits < total_cost:
            ar.events.append(f"{Colors.WARNING}Cannot afford Deep Clean. Cost: {total_cost} CRD.{Colors.ENDC}")
            return ar

        vulnerable = [r for r in self.regions if r.infected_nodes > 0 and not r.is_solidified]
        sacrifice = 0
        if not vulnerable:
            ar.events.append(f"{Colors.GOLD}All active nodes Solidified. Skipping sacrifice.{Colors.ENDC}")
        else:
            total_infected = sum(r.infected_nodes for r in self.regions)
            sacrifice = int(total_infected * 0.15)

        self.credits -= total_cost

        if sacrifice > 0:
            remaining = sacrifice
            random.shuffle(vulnerable)
            for r in vulnerable:
                if remaining <= 0: break
                take = min(r.infected_nodes, remaining)
                r.infected_nodes -= take
                remaining -= take
            
            actual_lost = sacrifice - remaining
            ar.events.append(f"{Colors.FAIL}SACRIFICE: Destroyed {actual_lost} nodes.{Colors.ENDC}")

        reduction = random.randint(25, 40)
        self.trace = max(0, self.trace - reduction)
        ar.events.append(f"{Colors.BLUE}LOGS PURGED: Trace reduced by {reduction}%.{Colors.ENDC}")
        ar.success = True
        return ar

    def action_wait(self):
        decay = 1.0
        self.trace = max(0, self.trace - decay)
        return ActionResult(success=True, events=[f"{Colors.BLUE}SYSTEM IDLE: Trace decayed by {decay}%.{Colors.ENDC}"])

    # --- Turn Loop & Passives ---
    def passive_check(self):
        self.turn += 1
        
        # 1. Passive Credit Drip
        if self.turn % 5 == 0:
            self.credits += 10
            self.log(f"{Colors.CYAN}DIVIDENDS: +10 CRD from shell accounts.{Colors.ENDC}")

        # 2. Black Swan (Secret Agent)
        if random.random() < 0.001:
            self.trace = 100.0
            descriptions = [
                "A shadow operative breached the physical server farm.",
                "Insider threat confirmed: Your lead engineer was a mole.",
                "Quantum decryption broke your master encryption key.",
                "Satellite triangulation pinpointed your uplink.",
                "A physical raid team has seized the control center."
            ]
            desc = random.choice(descriptions)
            self.log(f"{Colors.FAIL}{Colors.BOLD}BLACK SWAN EVENT: {desc} (+100.0% Trace){Colors.ENDC}")
        
        # 3. Standard Alerts
        elif random.random() < 0.15:
            spike = random.randint(2, 5)
            reason = random.choice(self.trace_excuses)
            scaled_spike = spike * self.trace_multiplier
            if scaled_spike > 5.0: scaled_spike = 5.0 # Cap
            applied = self.add_trace(scaled_spike, ignore_mask=True)
            self.log(f"{Colors.WARNING}ALERT: {reason} (+{applied:.1f}% Trace){Colors.ENDC}")

        # 4. Refugee Leak
        solidified_leak = sum(1 for r in self.regions if r.is_solidified)
        if solidified_leak > 0:
            applied = self.add_trace(solidified_leak, ignore_mask=True)
            self.log(f"{Colors.WARNING}LEAK: Solidified regions generated +{applied:.1f}% Trace.{Colors.ENDC}")

        # 5. DDoS Timer
        if self.ddos_timer > 0:
            self.ddos_timer -= 1
            if self.ddos_timer == 0:
                self.ddos_effectiveness = 0.0
                self.log(f"{Colors.WARNING}DDoS Masking Expired.{Colors.ENDC}")

        # 6. Hunter Killer (Saxxten)
        saxxten = self.regions[2]
        if saxxten.infected_nodes > 50 and not saxxten.is_solidified:
            if random.random() < 0.3:
                kill = int(saxxten.infected_nodes * 0.1)
                saxxten.infected_nodes -= kill
                self.log(f"{Colors.FAIL}HUNTER: Saxxten AI purged {kill} nodes.{Colors.ENDC}")

    # --- UI & Input ---
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
            pct = int(self.ddos_effectiveness * 100)
            print(f"STATUS: {Colors.CYAN}TRAFFIC MASKED ({pct}% Damper | {self.ddos_timer} turns){Colors.ENDC}")
        
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
        for i, r in enumerate(self.regions):
            print(f"[{i+1}] {r.status_bar}")
            
        print("-" * 50)
        print(f"{Colors.BOLD}LATEST LOGS:{Colors.ENDC}")
        for msg in self.history_log:
            print(f" > {msg}")
        print("-" * 50)

    def boot_sequence(self):
        clear_screen()
        print(Colors.CYAN + GAME_TITLE + Colors.ENDC)
        commands = [
            "[*] Initializing virtual stacks...",
            "[*] Injecting bootstrapped C2 beacons...",
            "[*] Synchronizing trait modules...",
            "[*] Stabilizing compute reservoirs...",
            f"{Colors.GREEN}[!] SYSTEM INITIALIZED. WELCOME, OPERATOR.{Colors.ENDC}"
        ]
        for cmd in commands:
            type_writer(cmd, 0.02)
            time.sleep(0.3)
        time.sleep(1)

    def run_terminal(self):
        self.boot_sequence()
        while not self.game_over:
            self.display_ui()
            
            print(f"\n{Colors.BOLD}AVAILABLE PROTOCOLS:{Colors.ENDC}")
            print(" [1-6] Target Region")
            print(" [C]   Deep Clean Logs (Costs CRD + Nodes)")
            print(" [W]   Wait / Idle (Passive Trace Decay)")
            print(" [S]   Save Game")
            print(" [L]   Load Game")
            print(" [Q]   Abort")
            
            choice = input(f"\n{Colors.BOLD}root@override:~$ {Colors.ENDC}").lower().strip()
            
            result = None

            if choice == 'q':
                break
            
            elif choice == 's':
                self.save_game()
                input(f"{Colors.BLUE}Press Enter to continue...{Colors.ENDC}")
                continue

            elif choice == 'l':
                if self.load_game():
                    input(f"{Colors.BLUE}Press Enter to continue...{Colors.ENDC}")
                else:
                    input(f"{Colors.FAIL}Press Enter to continue...{Colors.ENDC}")
                continue

            elif choice == 'w':
                result = self.action_wait()
            
            elif choice == 'c':
                result = self.action_purge_logs()
                
            elif choice in [str(i+1) for i in range(len(self.regions))]:
                idx = int(choice) - 1
                region = self.regions[idx]
                
                print(f"\n{Colors.UNDERLINE}TARGETING: {region.name}{Colors.ENDC}")
                costs = self.get_infect_costs()
                print(f" [1] SIGNAL INJECTION (Load: {costs['1'][0]}-{costs['1'][1]} CPU | 5-20%)")
                print(f" [2] PACKET FLOOD     (Load: {costs['2'][0]}-{costs['2'][1]} CPU | 25-50%)")
                print(f" [3] LOGIC BOMB       (Load: {costs['3'][0]}-{costs['3'][1]} CPU | 60-80%)")
                
                can_proxy = any(r.is_solidified for r in self.regions if r != region)
                if can_proxy:
                    print(f" {Colors.GOLD}[P] PROXY ATTACK     (Load: {costs['P']} CPU + 2000 CRD | STEALTH){Colors.ENDC}")
                
                print(" [4] RANSOMWARE (VAR. INTENSITY)")
                print(" [5] BOTNET DDOS (VAR. INTENSITY)")
                
                sub = input(f"{Colors.BOLD}Select Payload > {Colors.ENDC}").strip().upper()
                
                if sub in ['1', '2', '3', 'P']:
                    result = self.action_infect(idx, sub)
                elif sub == '4':
                    print(f"  [1] DATA SIPHON       (Req: 10 CPU | Low Yield/Trace)")
                    print(f"  [2] ENCRYPTION WARE   (Req: 40 CPU | Med Yield/Trace)")
                    print(f"  [3] INFRASTRUCTURE LOCK (Req: 80 CPU | High Yield/Trace)")
                    ran_sub = input(f"  {Colors.BOLD}Select Intensity > {Colors.ENDC}").strip()
                    if ran_sub in ['1', '2', '3']:
                        result = self.action_ransomware(idx, ran_sub)
                    else:
                        self.log("Invalid Ransomware selection.")
                        continue
                elif sub == '5':
                    print(f"  [1] SIMPLE DoS       (5 CRD  | 25% Mask | Req: 20 Nodes)")
                    print(f"  [2] DISTRIBUTED DoS  (20 CRD | 50% Mask | Req: 100 Nodes)")
                    print(f"  [3] BOTNET SWARM     (50 CRD | 75% Mask | Req: 300 Nodes)")
                    print(f"  [4] GLOBAL BLACKOUT  (150 CRD| 95% Mask | Req: 500 Nodes)")
                    ddos_sub = input(f"  {Colors.BOLD}Select Intensity > {Colors.ENDC}").strip()
                    if ddos_sub in ['1', '2', '3', '4']:
                        result = self.action_ddos(idx, ddos_sub)
                    else:
                        self.log("Invalid DDoS selection.")
                        continue
                else:
                    self.log("Invalid selection.")
                    continue

            if result:
                for event in result.events:
                    self.log(event)
                if result.success or choice == 'w' or (result and not result.success and choice not in ['q']):
                    self.passive_check()

            # Check End States
            if self.trace >= 100:
                self.display_ui()
                print(f"\n{Colors.FAIL}{Colors.BOLD}*** CRITICAL FAILURE: PHYSICAL TRACE CONFIRMED ***{Colors.ENDC}")
                break
            
            total_cap = sum(r.total_nodes for r in self.regions)
            if (self.compute - self.base_compute) >= total_cap:
                self.display_ui()
                print(f"\n{Colors.GREEN}{Colors.BOLD}*** GLOBAL SINGULARITY ACHIEVED ***{Colors.ENDC}")
                break

    # ---- Step API (monolithic) ----
    def step(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monolithic step interface for future FastAPI integration.
        action: one of 'infect', 'ransom', 'ddos', 'purge', 'wait', 'save', 'load'
        payload: dict containing parameters (e.g., region_index, intensity)
        Returns a JSON-serializable dict {state:..., events:...}
        """
        events: List[str] = []
        result: Optional[ActionResult] = None

        # Map actions
        if action == "infect":
            idx = int(payload.get("region_index", -1))
            intensity = payload.get("intensity", "med")
            use_proxy = bool(payload.get("proxy", False))
            result = self.action_infect(idx, intensity, use_proxy)
        elif action == "ransom":
            idx = int(payload.get("region_index", -1))
            result = self.action_ransomware(idx)
        elif action == "ddos":
            idx = int(payload.get("region_index", -1))
            result = self.action_ddos(idx)
        elif action == "purge":
            result = self.action_purge_logs()
        elif action == "wait":
            # small passive trace decay
            decay = payload.get("decay", 1.0)
            self.trace = clamp(self.trace - float(decay), 0.0, 100.0)
            events.append(f"SYSTEM IDLE: Trace decayed by {decay}%.")
            result = ActionResult(success=True, events=events, trace_change=-decay)
        elif action == "save":
            self.save(payload.get("filename", SAVE_FILE))
            result = ActionResult(success=True, events=[f"Saved to {SAVE_FILE}"])
        elif action == "load":
            ok = self.load(payload.get("filename", SAVE_FILE))
            result = ActionResult(success=ok, events=[f"Loaded {SAVE_FILE}" if ok else "Load failed"])
        else:
            result = ActionResult(success=False, events=[f"Unknown action: {action}"])

        # Post-action bookkeeping & global random events
        if result:
            events.extend(result.events)
            # integrate result effects already applied by the action methods

        # global passive mechanics
        # dividends every 5 turns
        if self.turn % 5 == 0:
            self.credits += 10
            events.append(f"DIVIDENDS: +10 credits from shell accounts.")

        # random mid-level alerts (15% chance)
        if random.random() < 0.15:
            spike = random.randint(2, 5)
            reason = random.choice([
                "ISP audit detected encrypted flows.",
                "Admin noticed anomalous task.",
                "Honeypot registered unusual traffic.",
                "Automated scanner flagged signature."
            ])
            scaled_spike = clamp(spike * self.trace_multiplier, 0.0, 5.0)
            self.trace = clamp(self.trace + scaled_spike, 0.0, 100.0)
            events.append(f"ALERT: {reason} (+{scaled_spike:.1f}% trace)")

        # solidified leak
        solid_leak = sum(2 for r in self.regions if r.is_solidified)
        if solid_leak > 0:
            self.trace = clamp(self.trace + solid_leak, 0.0, 100.0)
            events.append(f"LEAK: Solidified regions generated +{solid_leak}% trace.")

        # hunter-killer behavior (Saxxten)
        sax = next((r for r in self.regions if r.name == "Saxxten-36"), None)
        if sax and sax.infected_nodes > 30 and not sax.is_solidified:
            if random.random() < 0.25:
                kill = int(sax.infected_nodes * 0.08)
                sax.infected_nodes = max(0, sax.infected_nodes - kill)
                events.append(f"HUNTER: Saxxten AI purged {kill} nodes.")

        # ddos timer decay
        if self.ddos_timer > 0:
            self.ddos_timer -= 1
            if self.ddos_timer == 0:
                events.append("DDoS masking expired.")

        # check terminal states
        terminal = None
        if self.trace >= 100.0:
            terminal = {"outcome": "caught", "message": "Physical trace confirmed. Assets seized."}
            events.append("CRITICAL FAILURE: Trace 100% - You are caught.")
        else:
            # check global singularity
            total_capacity = sum(r.total_nodes for r in self.regions)
            if (self.compute - self.base_compute) >= total_capacity:
                terminal = {"outcome": "singularity", "message": "Global Singularity achieved. Humanity deprecated."}
                events.append("GLOBAL SINGULARITY ACHIEVED.")

        # update turn counter (do this at very end to reflect post-turn effects)
        self.turn += 1

        # compose state snapshot (lightweight)
        state = {
            "version": GAME_VERSION,
            "turn": self.turn,
            "credits": self.credits,
            "compute": self.compute,
            "trace": round(self.trace, 2),
            "trace_multiplier": round(self.trace_multiplier, 3),
            "ddos_timer": self.ddos_timer,
            "regions": [
                {
                    "name": r.name,
                    "infected_nodes": r.infected_nodes,
                    "total_nodes": r.total_nodes,
                    "is_solidified": r.is_solidified,
                    "defense": r.defense,
                    "trait": r.trait_name,
                    "infection_pct": round(r.infection_percentage, 2),
                } for r in self.regions
            ],
            "history": list(self.history[-self._max_history:]),
            "terminal": terminal,
        }

        return {"state": state, "events": events, "action_result": result.to_dict()}                

if __name__ == "__main__":
    game = GameEngine()
    game.run_terminal()