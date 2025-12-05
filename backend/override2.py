#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
import random
import math
import json
import os
import sys
import time
from typing import Dict, List, Any, Tuple, Optional

# ----------------------------
# CONFIG / UX TWEAKS
# ----------------------------
GAME_VERSION = "v2.0"
SAVE_FILE = "cyber_save.json"
RNG_SEED = None  # set an int for deterministic testing

if RNG_SEED is not None:
    random.seed(RNG_SEED)

# ----------------------------
# ANSI Colors (simple)
# ----------------------------
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

def type_writer(text: str, speed: float = 0.00):
    # optional terminal flair; keep speed = 0 for faster iteration
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if speed > 0:
            time.sleep(speed)
    print()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------
# HELPERS (balancing, RNG)
# ----------------------------

def tri(low: float, high: float) -> float:
    """Smoothed randomness using triangular distribution centered between low/high."""
    if low >= high:
        return low
    return random.triangular(low, high, (low + high) / 2.0)

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

# New trace multiplier: 1 + log2(1 + nodes/50) -> gentle, diminishing returns
def trace_multiplier_formula(total_infected_nodes: int) -> float:
    return min(1.0 + math.log2(1 + (total_infected_nodes / 100.0)), 10)

# Centralized success roll for balance
def roll_success(base_percent: float, difficulty: int, modifiers: float = 0.0) -> bool:
    """
    base_percent: 0-100 base chance
    difficulty: 1-10 (higher harder)
    modifiers: additive percentage modifier (positive helps)
    """
    chance = base_percent - (difficulty * 4.0) + modifiers  # tweakable scalar
    chance = clamp(chance, 1.0, 99.0)  # always some uncertainty
    roll = random.uniform(0.0, 100.0)
    return roll <= chance

# ----------------------------
# REGION / TRAIT SYSTEM
# ----------------------------

@dataclass
class Region:
    name: str
    total_nodes: int
    defense: int  # 1-10
    infected_nodes: int = 0
    trait_name: str = "GENERIC"
    # Optional properties for extensibility
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_solidified(self) -> bool:
        return self.infected_nodes >= self.total_nodes

    @property
    def infection_percentage(self) -> float:
        if self.total_nodes <= 0:
            return 0.0
        return (self.infected_nodes / self.total_nodes) * 100.0

    def status_bar_text(self) -> str:
        percent = self.infection_percentage
        if self.is_solidified:
            color = Colors.GOLD
            status = "DOMINATED"
        else:
            color = Colors.GREEN if percent > 0 else Colors.FAIL
            status = f"{self.infected_nodes}/{self.total_nodes}"
        return f"{self.name.ljust(20)} | {color}{status.rjust(9)}{Colors.ENDC} | Def: {self.defense} | {self.trait_name}"

# Traits are composable small classes with deterministic methods
class Trait:
    """Base trait. Override desired hooks."""
    name = "BASE_TRAIT"

    def on_ransom_multiplier(self, base_mult: float) -> float:
        return base_mult

    def on_infect_gain_multiplier(self, base_mult: float) -> float:
        return base_mult

    def on_infect_trace_modifier(self, trace: float) -> float:
        return trace

    def on_ddos_effect(self, engine, region: Region) -> Dict[str, Any]:
        """Return dict describing ddos side-effects (e.g., extra mask, risk)."""
        return {}

# Concrete trait implementations (rebalanced)
class CorporateVaultTrait(Trait):
    name = "CORPORATE VAULT"
    def on_ransom_multiplier(self, base_mult: float) -> float:
        return base_mult * 2.0  # big payday, slightly reduced trace benefit
    def on_infect_trace_modifier(self, trace: float) -> float:
        return trace * 1.5  # high-profile => more trace

class IoTSwarmTrait(Trait):
    name = "IOT SWARM"
    def on_infect_gain_multiplier(self, base_mult: float) -> float:
        return base_mult * 1.75  # lots of cheap nodes
    def on_infect_trace_modifier(self, trace: float) -> float:
        return trace * 0.9  # noisy, but distributed => slightly lower trace per node

class HunterKillerTrait(Trait):
    name = "HUNTER KILLER"
    def on_infect_gain_multiplier(self, base_mult: float) -> float:
        return base_mult * 0.9  # hard to infect
    def on_infect_trace_modifier(self, trace: float) -> float:
        return trace * 2.0     # getting noticed is dangerous

class OrbitalStackTrait(Trait):
    name = "ORBITAL STACK"
    def on_infect_trace_modifier(self, trace: float) -> float:
        return trace * 0.8  # space latency hides some trace

class DeepWebTrait(Trait):
    name = "DEEP WEB"
    def on_ransom_multiplier(self, base_mult: float) -> float:
        return base_mult * 0.9  # messy, less payout but lower trace
    def on_infect_trace_modifier(self, trace: float) -> float:
        return trace * 0.8

class QuantumCoreTrait(Trait):
    name = "QUANTUM CORE"
    # Unstable. Can occasionally (rare) double gains or cause a penalty
    def on_infect_gain_multiplier(self, base_mult: float) -> float:
        return base_mult  # neutral baseline; engine can trigger random bursts

# Region factory with rebalanced stats (choice B)
def build_default_regions() -> List[Tuple[Region, Trait]]:
    # Rebalanced: total_nodes reasonable, defense scaled so progression feels tactical.
    return [
        (Region("Elystrion", 600, 5, trait_name="CORPORATE VAULT"), CorporateVaultTrait()),
        (Region("Sylthara Bloom", 2000, 3, trait_name="IOT SWARM"), IoTSwarmTrait()),
        (Region("Saxxten-36", 450, 8, trait_name="HUNTER KILLER"), HunterKillerTrait()),
        (Region("Valkyrine Ridge", 550, 7, trait_name="ORBITAL STACK"), OrbitalStackTrait()),
        (Region("Tartarus Sector", 1400, 2, trait_name="DEEP WEB"), DeepWebTrait()),
        (Region("Coda Labyrinth", 700, 6, trait_name="QUANTUM CORE"), QuantumCoreTrait()),
    ]

# ----------------------------
# ACTION RESULT / EVENT MODEL
# ----------------------------
@dataclass
class ActionResult:
    success: bool
    events: List[str] = field(default_factory=list)
    trace_change: float = 0.0
    credits_change: int = 0
    node_change: Dict[str, int] = field(default_factory=dict)  # region name -> delta

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "events": self.events,
            "trace_change": self.trace_change,
            "credits_change": self.credits_change,
            "node_change": self.node_change,
        }

# ----------------------------
# GAME ENGINE
# ----------------------------
class GameEngine:
    def __init__(self):
        # regions: keep pairing with trait objects
        region_pairs = build_default_regions()
        self.regions: List[Region] = [r for r, t in region_pairs]
        self.traits: Dict[str, Trait] = {r.name: t for r, t in region_pairs}

        # State variables
        self.credits: int = 120  # slightly raised starting funds
        self.base_compute: int = 60  # baseline CPU capacity
        self.trace: float = 0.0
        self.turn: int = 1
        self.ddos_timer: int = 0
        self.history: List[str] = []
        self._max_history = 8

        # Balancing knobs
        self.infect_base_load_pct = (0.05, 0.20, 0.60)  # low, med, high intensity ranges of compute fraction
        self.infect_base_trace_ranges = {
            "low": (0.4, 1.2),
            "med": (1.0, 2.6),
            "high": (3.0, 6.0),
            "proxy": (0.05, 0.25),
        }
        self.ransom_required_load = 30
        self.ddos_cost_credits = 5

    # ---- Derived properties ----
    @property
    def compute(self) -> int:
        total_infected = sum(r.infected_nodes for r in self.regions)
        return int(self.base_compute + total_infected)

    @property
    def total_infected(self) -> int:
        return sum(r.infected_nodes for r in self.regions)

    @property
    def trace_multiplier(self) -> float:
        return trace_multiplier_formula(self.total_infected)

    # ---- Logging ----
    def log(self, msg: str):
        self.history.append(msg)
        if len(self.history) > self._max_history:
            self.history.pop(0)

    # ---- Persistence ----
    def save(self, filename: str = SAVE_FILE):
        payload = {
            "credits": self.credits,
            "base_compute": self.base_compute,
            "trace": self.trace,
            "turn": self.turn,
            "ddos_timer": self.ddos_timer,
            "regions": [asdict(r) for r in self.regions],
        }
        with open(filename, "w") as f:
            json.dump(payload, f, indent=2)
        self.log(f"{Colors.BLUE}Game saved to {filename}.{Colors.ENDC}")

    def load(self, filename: str = SAVE_FILE) -> bool:
        if not os.path.exists(filename):
            self.log(f"{Colors.WARNING}No save found at {filename}.{Colors.ENDC}")
            return False
        with open(filename, "r") as f:
            payload = json.load(f)
        self.credits = payload.get("credits", self.credits)
        self.base_compute = payload.get("base_compute", self.base_compute)
        self.trace = payload.get("trace", self.trace)
        self.turn = payload.get("turn", self.turn)
        self.ddos_timer = payload.get("ddos_timer", self.ddos_timer)
        region_payloads = payload.get("regions", [])
        for rp in region_payloads:
            for r in self.regions:
                if r.name == rp.get("name"):
                    r.infected_nodes = rp.get("infected_nodes", r.infected_nodes)
        self.log(f"{Colors.BLUE}Game loaded from {filename}.{Colors.ENDC}")
        return True

    # ---- Core Actions (return ActionResult) ----
    def action_infect(self, region_index: int, intensity: str, use_proxy: bool = False) -> ActionResult:
        """
        intensity: 'low', 'med', 'high'
        use_proxy: whether to consume solidified proxy routing
        """
        ar = ActionResult(success=False)
        if not (0 <= region_index < len(self.regions)):
            ar.events.append("Invalid region.")
            return ar
        region = self.regions[region_index]
        trait = self.traits.get(region.name, Trait())

        if region.is_solidified:
            ar.events.append(f"{region.name} already solidified.")
            return ar

        # compute requirement based on intensity fraction
        cap = self.compute
        frac = 0.0
        trace_range = (0.0, 0.0)
        gain_mult = 1.0

        if intensity == "low":
            frac = self.infect_base_load_pct[0]
            trace_range = self.infect_base_trace_ranges["low"]
            gain_mult = 1.0
        elif intensity == "med":
            frac = self.infect_base_load_pct[1]
            trace_range = self.infect_base_trace_ranges["med"]
            gain_mult = 2.0
        elif intensity == "high":
            frac = self.infect_base_load_pct[2]
            trace_range = self.infect_base_trace_ranges["high"]
            gain_mult = 4.0
        elif intensity == "proxy" and use_proxy:
            # fixed cost for proxy route
            frac = 0.40
            trace_range = self.infect_base_trace_ranges["proxy"]
            gain_mult = 1.8
        else:
            ar.events.append("Invalid intensity selection.")
            return ar

        load_req = max(1, int(cap * frac))
        if self.compute < load_req:
            ar.events.append(f"Insufficient compute (need {load_req} CPU).")
            return ar

        # if proxy chosen, ensure at least one other region is solidified
        if intensity == "proxy":
            if not any(r.is_solidified and r != region for r in self.regions):
                ar.events.append("No proxy available (no other solidified region).")
                return ar
            # proxies cost credits — small tax
            proxy_credit_cost = 250
            if self.credits < proxy_credit_cost:
                ar.events.append(f"Insufficient credits for proxy (need {proxy_credit_cost}).")
                return ar
            self.credits -= proxy_credit_cost
            ar.credits_change -= proxy_credit_cost

        # base chance
        base_chance = 78.0  # tuned baseline
        if region.name == "Saxxten-36":
            region_def_adj = region.defense + 2
        else:
            region_def_adj = region.defense

        # solidified buff increases chance slightly
        solidified_buff = sum(6 for r in self.regions if r.is_solidified)
        # compute final chance
        if intensity == "proxy":
            base_chance += 12.0

        success = roll_success(base_chance, region_def_adj, solidified_buff)

        if success:
            # determine node gain with smoothing
            base_gain = int(load_req * 0.75 * gain_mult)
            base_gain = max(4, base_gain)
            # trait modifies node gain
            base_gain = int(base_gain * trait.on_infect_gain_multiplier(1.0))
            # cap to region remaining nodes
            actual_gain = min(base_gain, region.total_nodes - region.infected_nodes)
            region.infected_nodes += actual_gain
            ar.node_change[region.name] = actual_gain

            # trace calculation (smoothed and trait-modified)
            base_trace = tri(trace_range[0], trace_range[1])
            scaled_trace = base_trace * self.trace_multiplier
            scaled_trace = trait.on_infect_trace_modifier(scaled_trace)
            # apply special region multipliers
            if region.name == "Elystrion":
                scaled_trace *= 1.25
            scaled_trace = clamp(scaled_trace, 0.0, 50.0)

            self.trace = clamp(self.trace + scaled_trace, 0.0, 100.0)
            ar.trace_change = scaled_trace
            ar.success = True
            ar.events.append(f"SUCCESS: Infected {actual_gain} nodes in {region.name}. (+{scaled_trace:.1f}% trace)")

            if region.is_solidified:
                ar.events.append(f"*** {region.name} SOLIDIFIED! Nodes hardened. ***")
        else:
            # failure: small trace, smoothing, can be amplified by traits
            fail_trace = tri(1.0, 3.0) * self.trace_multiplier
            fail_trace = trait.on_infect_trace_modifier(fail_trace)
            fail_trace = clamp(fail_trace, 0.0, 50.0)
            self.trace = clamp(self.trace + fail_trace, 0.0, 100.0)
            ar.trace_change = fail_trace
            ar.events.append(f"FAILURE: Infection attempt blocked. (+{fail_trace:.1f}% trace)")
            ar.success = False

        return ar

    def action_ransomware(self, region_index: int) -> ActionResult:
        ar = ActionResult(success=False)
        if not (0 <= region_index < len(self.regions)):
            ar.events.append("Invalid region.")
            return ar
        region = self.regions[region_index]
        trait = self.traits.get(region.name, Trait())

        if region.infected_nodes < 10:
            ar.events.append(f"Not enough infected nodes in {region.name} to run ransomware.")
            return ar
        if self.compute < self.ransom_required_load:
            ar.events.append(f"Insufficient compute (need {self.ransom_required_load}).")
            return ar

        # compute cash reward
        base_cash = int(region.infected_nodes * 0.45)
        cash = int(base_cash * trait.on_ransom_multiplier(1.0))
        # trace: smooth triangular * multiplier
        base_trace = tri(4.0, 9.0) * trait.on_infect_trace_modifier(1.0)
        scaled_trace = base_trace * self.trace_multiplier
        scaled_trace = clamp(scaled_trace, 0.0, 50.0)

        self.credits += cash
        self.trace = clamp(self.trace + scaled_trace, 0.0, 100.0)
        ar.credits_change = cash
        ar.trace_change = scaled_trace
        ar.success = True
        ar.events.append(f"RANSOMWARE: Extracted {cash} credits from {region.name}. (+{scaled_trace:.1f}% trace)")
        return ar

    def action_ddos(self, region_index: int) -> ActionResult:
        ar = ActionResult(success=False)
        if not (0 <= region_index < len(self.regions)):
            ar.events.append("Invalid region.")
            return ar
        region = self.regions[region_index]
        trait = self.traits.get(region.name, Trait())

        if region.infected_nodes < 40:
            ar.events.append(f"Need at least 40 nodes in {region.name} to attempt a DDoS.")
            return ar
        if self.credits < self.ddos_cost_credits:
            ar.events.append("Insufficient credits for DDoS.")
            return ar

        self.credits -= self.ddos_cost_credits
        ar.credits_change -= self.ddos_cost_credits

        success_chance = 80.0 + (5.0 if region.is_solidified else 0.0)
        success = random.uniform(0, 100) < success_chance

        if success:
            # set a masking timer (smoothed to 2-3 turns)
            self.ddos_timer = random.choice([2, 3])
            ar.success = True
            ar.events.append(f"DDoS success: traffic masked for {self.ddos_timer} turns.")
            # small cost in nodes (botnet strain)
            lost = max(1, int(region.infected_nodes * 0.02))
            region.infected_nodes = max(0, region.infected_nodes - lost)
            ar.node_change[region.name] = -lost
        else:
            # fail cost: nodes lost and trace spike ignoring mask
            lost = int(region.infected_nodes * 0.08)
            region.infected_nodes = max(0, region.infected_nodes - lost)
            fail_trace = tri(3.0, 7.0) * self.trace_multiplier
            fail_trace = trait.on_infect_trace_modifier(fail_trace)
            fail_trace = clamp(fail_trace, 0.0, 50.0)
            self.trace = clamp(self.trace + fail_trace, 0.0, 100.0)
            ar.node_change[region.name] = -lost
            ar.trace_change = fail_trace
            ar.events.append(f"DDoS failed: lost {lost} nodes. (+{fail_trace:.1f}% trace)")
            ar.success = False

        return ar

    def action_purge_logs(self) -> ActionResult:
        ar = ActionResult(success=False)
        base_cost = 55
        trace_tax = int(self.trace * 2)
        vulnerable_nodes = sum(r.infected_nodes for r in self.regions if r.infected_nodes > 0 and not r.is_solidified)
        cost_per_node = 1  # or 2 CRD per node, tuneable
        total_cost = base_cost + int(self.trace * 2) + vulnerable_nodes * cost_per_node
        # total_cost = base_cost + trace_tax
        if self.credits < total_cost:
            ar.events.append(f"Cannot afford purge (need {total_cost} credits).")
            return ar

        vulnerable = [r for r in self.regions if r.infected_nodes > 0 and not r.is_solidified]
        total_infected = sum(r.infected_nodes for r in self.regions)
        sacrifice = 0
        if vulnerable:
            sacrifice = int(total_infected * 0.12)  # balanced sacrifice
        self.credits -= total_cost
        ar.credits_change -= total_cost

        if sacrifice > 0:
            remaining = sacrifice
            random.shuffle(vulnerable)
            for r in vulnerable:
                if remaining <= 0:
                    break
                take = min(r.infected_nodes, remaining)
                r.infected_nodes -= take
                remaining -= take
            actual_lost = sacrifice - remaining
            ar.node_change = {r.name: r.infected_nodes for r in self.regions if r.infected_nodes}  # provide new snapshot
            ar.events.append(f"SACRIFICE: Destroyed {actual_lost} nodes to erase traces.")
        else:
            ar.events.append("No vulnerable nodes found; no sacrifice required.")

        reduction = random.randint(18, 36)
        self.trace = clamp(self.trace - reduction, 0.0, 100.0)
        ar.trace_change = -reduction
        ar.success = True
        ar.events.append(f"LOGS PURGED: Trace reduced by {reduction}%.")
        return ar

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

    # ---- CLI adapter (temporary) ----
    def display_ui(self):
        clear_screen()
        print(Colors.HEADER + f"--- OPERATION CYCLE: {self.turn} --- {GAME_VERSION}" + Colors.ENDC)
        print(f"CAPACITY: {Colors.CYAN}{int(self.compute)} CPU{Colors.ENDC} | FUNDS: {Colors.GREEN}{self.credits} CRD")
        mult = self.trace_multiplier
        color = Colors.GREEN
        if mult > 3.0: color = Colors.WARNING
        if mult > 8.0: color = Colors.FAIL
        print(f"NETWORK SIGNATURE: {color}{mult:.2f}x Multiplier{Colors.ENDC}")
        if self.ddos_timer > 0:
            print(f"STATUS: {Colors.CYAN}TRAFFIC MASKED (DDoS Active: {self.ddos_timer} turns){Colors.ENDC}")
        solidified_count = sum(1 for r in self.regions if r.is_solidified)
        if solidified_count > 0:
            print(f"STATUS: {Colors.GOLD}PROXY ROUTING ACTIVE ({solidified_count} Regions Solidified){Colors.ENDC}")

        # trace bar
        bar_len = 36
        filled = int((self.trace / 100) * bar_len)
        bar_color = Colors.GREEN
        if self.trace > 40: bar_color = Colors.WARNING
        if self.trace > 80: bar_color = Colors.FAIL
        bar_str = "#" * filled + "-" * (bar_len - filled)
        print(f"GLOBAL TRACE: {bar_color}[{bar_str}] {self.trace:.1f}%{Colors.ENDC}\n")

        print(Colors.UNDERLINE + "SECTORS" + Colors.ENDC)
        for i, r in enumerate(self.regions):
            print(f"[{i+1}] {r.status_bar_text()}")

        print("-" * 60)
        print(f"{Colors.BOLD}LATEST LOGS:{Colors.ENDC}")
        for msg in self.history:
            print(f" > {msg}")
        print("-" * 60)

    def run_terminal(self):
        self.boot_sequence()
        while True:
            self.display_ui()
            print("\n[ACTIONS]")
            print(" [1-6] Target region")
            print(" [C]   Purge logs")
            print(" [W]   Wait/Idle")
            print(" [S]   Save")
            print(" [L]   Load")
            print(" [Q]   Quit")
            choice = input("\nroot@override:~$ ").strip().lower()
            if choice == "q":
                print("Aborting session.")
                break
            elif choice == "s":
                self.save()
                input("Press Enter...")
                continue
            elif choice == "l":
                self.load()
                input("Press Enter...")
                continue
            elif choice == "w":
                resp = self.step("wait", {"decay": 1.0})
                for e in resp["events"]:
                    self.log(e)
                input("Press Enter...")
                continue
            elif choice == "c":
                resp = self.step("purge", {})
                for e in resp["events"]:
                    self.log(e)
                input("Press Enter...")
                continue
            elif choice in [str(i) for i in range(1, len(self.regions) + 1)]:
                idx = int(choice) - 1
                target = self.regions[idx]
                print(f"\nTarget: {target.name}")
                print(" [1] Infect (low)")
                print(" [2] Infect (med)")
                print(" [3] Infect (high)")
                print(" [4] Infect (proxy) [requires solidified proxy + credits]")
                print(" [5] Ransomware")
                print(" [6] DDoS")
                sub = input("Select payload > ").strip()
                if sub == "1":
                    resp = self.step("infect", {"region_index": idx, "intensity": "low"})
                elif sub == "2":
                    resp = self.step("infect", {"region_index": idx, "intensity": "med"})
                elif sub == "3":
                    resp = self.step("infect", {"region_index": idx, "intensity": "high"})
                elif sub == "4":
                    resp = self.step("infect", {"region_index": idx, "intensity": "proxy", "proxy": True})
                elif sub == "5":
                    resp = self.step("ransom", {"region_index": idx})
                elif sub == "6":
                    resp = self.step("ddos", {"region_index": idx})
                else:
                    self.log("Invalid payload.")
                    input("Press Enter...")
                    continue
                # apply events to local history
                for e in resp["events"]:
                    self.log(e)
                # check terminal state
                if resp["state"]["terminal"] is not None:
                    self.display_ui()
                    print(resp["state"]["terminal"]["message"])
                    break
                input("Press Enter...")
                continue
            else:
                self.log("Unknown command.")
                input("Press Enter...")

    def boot_sequence(self):
        clear_screen()
        banner = f"""
  ____  _   _  __  __  ____  _____  ____  _   _ 
 |  _ \| | | ||  \/  |/ __ \|  __ \|  _ \| \ | |
 | |_) | | | || \  / | |  | | |__) | |_) |  \| |
 |  _ <| | | || |\/| | |  | |  _  /|  _ <| . ` |
 | |_) | |_| || |  | | |__| | | \ \| |_) | |\  |
 |____/ \___/ |_|  |_|\____/|_|  \_\____/|_| \_|
           -- PROTOCOL: EXPANSION v2.0 --
"""
        type_writer(Colors.CYAN + banner + Colors.ENDC, speed=0.0)
        cmds = [
            "[*] Initializing virtual stacks...",
            "[*] Injecting bootstrapped C2 beacons...",
            "[*] Synchronizing trait modules...",
            "[*] Stabilizing compute reservoirs...",
            "[*] SYSTEM INITIALIZED. WELCOME, OPERATOR."
        ]
        for c in cmds:
            type_writer(c, 0.01)

# ----------------------------
# If run as script, launch terminal adapter
# ----------------------------
def main():
    engine = GameEngine()
    # quick hint: engine.step(action,payload) -> good for FastAPI
    engine.run_terminal()

if __name__ == "__main__":
    main()