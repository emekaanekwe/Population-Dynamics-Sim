"""
Step 1: well-mixed ODE model of two competing protocell populations.

Target behaviour (qualitative, from Katla, Lin & Perez-Mercader 2023,
Cell Rep. Phys. Sci. 4, 101359):

  * WZ (ZnTPP-doped) and WOZ (undoped) each grow when cultured separately.
  * Mixed 1:1, WZ keeps growing while WOZ declines  -> competitive exclusion
    (their Fig. 4C, overlaid on Gause's paramecia in Fig. 4D).
  * WZ population growth is strongly light-dependent: green > blue > orange,
    4 s pulse > 1 s pulse, 10 s period > 15 s > 30 s, 47 mW > 32 mW > 20 mW
    (their Fig. 2B-E). WOZ is nearly insensitive to all of these (Fig. S6).
  * WZ growth increases with added HPMA, 10% > 5% > 0% (Fig. 3C); WOZ barely
    responds (Fig. 3D).
  * The three-stage shape of the WZ curve: fast rise, stall around ~2,400 s as
    local HPMA is depleted, then slow re-acceleration as monomer diffuses in
    from the surrounding unilluminated region (99.6% of the slide).

MODEL
-----
Chemostat-style resource competition (Monod kinetics) on a single shared
resource S = HPMA monomer in the illuminated patch.

    mu_i(S)   = mu_max_i * L_i * S / (K_i + S)          growth rate of species i
    dN_i/dt   = mu_i * N_i - delta_i * N_i              vesicles, birth minus decay
    dS/dt     = -sum_i (mu_i * N_i / Y_i) + d*(R - S)   consumption + diffusive recharge
    dR/dt     = -(v * d) * (R - S)                      finite surrounding reservoir

N_i counts vesicles rather than tracking biomass. Reproduction is folded into
mu: in the real system, consumed monomer extends the hydrophobic block, congests
the lumen, and a fraction of amphiphiles is squeezed out to nucleate a daughter.
Here that whole chain is one yield coefficient Y_i. Step 2 (spatial) and step 3
(individual vesicles) unfold it.

L_i is the light drive, the player's main knob. It is normalised to 1.0 at the
paper's baseline conditions (550 nm, 1 s pulse, 10 s period, 20.46 mW).

WHAT THIS MODEL DELIBERATELY DOES NOT HAVE
------------------------------------------
  * Space. The paper's mixture experiment invokes an HPMA gradient that pulls
    monomer and free amphiphiles toward the faster-polymerising population.
    A well-mixed ODE cannot represent that. Exclusion here comes purely from
    the R* rule (the species that can persist at lower S wins). If the real
    mechanism needs the gradient, this model will under-predict how fast WOZ
    collapses -- which is itself a useful thing to find out.
  * Heredity and variation. Both populations are fixed types. Nothing mutates.
  * Vesicle size. The paper tracks mean diameter as a second observable; adding
    it requires at least a two-state model (number and mean size).

Requires: numpy, scipy, matplotlib.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp


# ---------------------------------------------------------------------------
# Environment: the knobs a player gets to turn
# ---------------------------------------------------------------------------

# ZnTPP light-harvesting efficiency vs wavelength. These are NOT spectroscopic
# values -- they are set to reproduce the order
# ing and rough spacing of Fig. 2B
# (green best, blue intermediate, orange poor). Replace with real ZnTPP
# absorbance if you digitise their Fig. S4.
_ZNTPP_EFFICIENCY = {
    450.0: 0.30,
    470.0: 0.45,
    510.0: 0.80,
    550.0: 1.00,
    570.0: 0.55,
    585.0: 0.15,
    620.0: 0.05,
}

_REF_POWER_MW = 20.46   # lowest power used in Fig. 2E
_REF_DUTY = 1.0 / 10.0  # 1 s pulse, 10 s period -- the paper's default


@dataclass
class Environment:
    """Illumination and feeding conditions. This is the player's control panel."""

    wavelength_nm: float = 550.0
    pulse_duration_s: float = 1.0
    pulse_period_s: float = 10.0
    power_mw: float = 20.46
    extra_food_frac: float = 0.0  # 0.05 and 0.10 in the paper's Fig. 3C/D

    def wavelength_grid(self) -> np.ndarray:
        return np.array(sorted(_ZNTPP_EFFICIENCY))

    def photon_drive(self) -> float:
        """Dimensionless light input, 1.0 at the paper's baseline conditions.

        Pulsed illumination is time-averaged rather than resolved. That is safe
        here because the pulse period (10-30 s) is thousands of times shorter
        than the population timescale (~10^4 s).
        """
        grid = self.wavelength_grid()
        vals = np.array([_ZNTPP_EFFICIENCY[w] for w in grid])
        efficiency = float(np.interp(self.wavelength_nm, grid, vals))

        duty = self.pulse_duration_s / self.pulse_period_s
        duty = min(duty, 1.0)
        drive = efficiency * (duty / _REF_DUTY) * (self.power_mw / _REF_POWER_MW) 

        return drive


# ---------------------------------------------------------------------------
# Species
# ---------------------------------------------------------------------------

@dataclass
class Species:
    """One protocell population.

    light_exponent controls how much the photon drive matters. WZ carries the
    ZnTPP photocatalyst and is strongly light-limited (exponent near 1). WOZ has
    only the iniferter's own weak absorption, so its exponent is small -- this is
    the model's version of the paper's observation that WOZ barely responds to
    changes in illumination (Fig. S6).
    """

    name: str
    mu_max: float          # 1/s, maximum specific reproduction rate
    k_half: float          # half-saturation monomer concentration
    yield_coeff: float     # vesicles produced per unit monomer, at saturating light
    decay: float           # 1/s, loss rate (membrane degradation, collapse)
    light_exponent: float
    yield_light_half: float = 0.8  # photon drive at which yield is half-maximal

    def light_factor(self, drive: float) -> float:
        return float(drive ** self.light_exponent)

    def effective_yield(self, drive: float) -> float:
        """Vesicles produced per unit monomer, gated by light.

        This is the model's most important non-obvious ingredient. Reproduction
        in the real system is not just "eat monomer, make daughter": a vesicle
        only ejects amphiphiles once its hydrophobic block has extended enough to
        congest the lumen. Under weak illumination, chains extend slowly and much
        of the consumed monomer goes into vesicles that never cross the ejection
        threshold within the experiment. So light changes not only how fast food
        is eaten but how much of it converts into new vesicles.

        Without this term the model is purely supply-limited: whatever monomer
        arrives eventually gets eaten regardless of illumination, the final
        population is set by total food alone, and the paper's Fig. 2B-E
        light-dependence vanishes. That failure is worth reproducing once
        yourself -- comment this out and watch the sweeps collapse.
        """
        light = self.light_factor(drive)
        return self.yield_coeff * light / (light + self.yield_light_half)

    def growth_rate(self, s: float, drive: float) -> float:
        s = max(s, 0.0)
        return self.mu_max * self.light_factor(drive) * s / (self.k_half + s)

    def r_star(self, drive: float) -> float:
        """Break-even monomer level: the S at which growth exactly offsets decay.

        The classic competitive-exclusion criterion. Whichever species has the
        lower R* drives S down past its rival's break-even point and excludes it.
        Worth printing -- it predicts the winner before you integrate anything.
        """
        mu_eff = self.mu_max * self.light_factor(drive)
        if mu_eff <= self.decay:
            return np.inf
        return self.k_half * self.decay / (mu_eff - self.decay)


def default_species() -> tuple[Species, Species]:
    """WZ and WOZ, tuned so the baseline run reproduces the paper's shapes."""
    wz = Species(
        name="WZ (with ZnTPP)",
        mu_max=7.0e-4,
        k_half=0.18,
        yield_coeff=2.2e4,
        decay=3.0e-6,
        light_exponent=1.0,
    )
    woz = Species(
        name="WOZ (no ZnTPP)",
        mu_max=2.4e-4,
        k_half=0.30,
        yield_coeff=6.2e3,
        decay=3.0e-6,
        light_exponent=0.15,
    )
    return wz, woz


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

@dataclass
class SimConfig:
    t_end: float = 43_150.0        # the paper ran to 43,150 s
    n_points: int = 2000
    s0: float = 1.0                # monomer in the illuminated patch
    reservoir0: float = 1.0        # monomer in the surrounding dark region
    exchange_rate: float = 2.2e-5  # 1/s, diffusive recharge of the patch
    volume_ratio: float = 0.004    # patch is 0.4% of the unilluminated area
    n0: float = 10_000.0           # starting vesicle count per population
    species: tuple = field(default_factory=default_species)


def simulate(env: Environment, cfg: SimConfig, n_init: tuple[float, float] | None = None):
    """Integrate the system.

    `n_init` is the starting vesicle count for (WZ, WOZ). Use (N0, 0) or (0, N0)
    for the separate cultures and (N0/2, N0/2) for the 1:1 v/v mixture -- mixing
    two stock solutions in equal volumes halves each population's density, which
    is why the paper's mixed WZ curve sits below its separate one even before
    competition bites.
    """
    wz, woz = cfg.species
    drive = env.photon_drive()
    s0 = cfg.s0 * (1.0 + env.extra_food_frac)
    r0 = cfg.reservoir0 * (1.0 + env.extra_food_frac)

    if n_init is None:
        n_init = (cfg.n0, cfg.n0)
    y0 = [float(n_init[0]), float(n_init[1]), s0, r0]

    y_wz = wz.effective_yield(drive)
    y_woz = woz.effective_yield(drive)

    def rhs(_t, y):
        n_wz, n_woz, s, r = y
        s = max(s, 0.0)

        mu_wz = wz.growth_rate(s, drive)
        mu_woz = woz.growth_rate(s, drive)

        dn_wz = (mu_wz - wz.decay) * n_wz
        dn_woz = (mu_woz - woz.decay) * n_woz

        consumption = mu_wz * n_wz / y_wz + mu_woz * n_woz / y_woz
        recharge = cfg.exchange_rate * (r - s)

        ds = -consumption + recharge
        dr = -cfg.volume_ratio * recharge

        return [dn_wz, dn_woz, ds, dr]

    t_eval = np.linspace(0.0, cfg.t_end, cfg.n_points)
    sol = solve_ivp(rhs, (0.0, cfg.t_end), y0, t_eval=t_eval,
                    method="LSODA", rtol=1e-8, atol=1e-10)
    if not sol.success:
        raise RuntimeError(f"integration failed: {sol.message}")

    return {
        "t": sol.t,
        "wz": sol.y[0],
        "woz": sol.y[1],
        "s": sol.y[2],
        "reservoir": sol.y[3],
        "drive": drive,
    }


# ---------------------------------------------------------------------------
# Reproducing the paper's panels
# ---------------------------------------------------------------------------

def figure_competition(env: Environment, cfg: SimConfig, path: str):
    """Recreate the structure of the paper's Fig. 4A-C: each population alone,
    then the 1:1 mixture."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    alone_wz = simulate(env, cfg, n_init=(cfg.n0, 0.0))
    alone_woz = simulate(env, cfg, n_init=(0.0, cfg.n0))
    mixed = simulate(env, cfg, n_init=(cfg.n0 / 2, cfg.n0 / 2))

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

    axes[0].plot(alone_wz["t"], alone_wz["wz"] - cfg.n0, "k-", label="separately")
    axes[0].plot(mixed["t"], mixed["wz"] - cfg.n0 / 2, "g-", label="mixed")
    axes[0].set_title("WZ population")

    axes[1].plot(alone_woz["t"], alone_woz["woz"] - cfg.n0, "r-", label="separately")
    axes[1].plot(mixed["t"], mixed["woz"] - cfg.n0 / 2, "b-", label="mixed")
    axes[1].set_title("WOZ population")

    axes[2].plot(mixed["t"], mixed["wz"] - cfg.n0 / 2, "g-", label="WZ")
    axes[2].plot(mixed["t"], mixed["woz"] - cfg.n0 / 2, "b-", label="WOZ")
    axes[2].axhline(0.0, color="0.7", lw=0.8)
    axes[2].set_title("1:1 mixture")

    for ax in axes:
        ax.set_xlabel("time (s)")
        ax.set_ylabel(r"growth in population $\Delta N$")
        ax.legend(frameon=False)

    fig.suptitle("Competitive exclusion from pure resource competition "
                 "(cf. Katla et al. 2023, Fig. 4A-C)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def figure_environment_sweeps(cfg: SimConfig, path: str):
    """Recreate the structure of Fig. 2B-E and 3C: the player's knobs."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(19, 4.0), sharey=True)

    sweeps = [
        ("wavelength (nm)", "wavelength_nm", [470.0, 550.0, 585.0]),
        ("pulse duration (s)", "pulse_duration_s", [1.0, 4.0]),
        ("pulse period (s)", "pulse_period_s", [10.0, 15.0, 30.0]),
        ("light power (mW)", "power_mw", [20.46, 31.70, 47.20]),
    ]

    for ax, (label, attr, values) in zip(axes, sweeps):
        for v in values:
            env = Environment(**{attr: v})
            out = simulate(env, cfg, n_init=(cfg.n0, 0.0))
            ax.plot(out["t"], out["wz"] / cfg.n0, label=f"{v:g}")
        ax.set_title(label)
        ax.set_xlabel("time (s)")
        ax.legend(frameon=False, title=label.split(" (")[0])

    axes[0].set_ylabel(r"normalised population $N/N_0$")
    fig.suptitle("WZ response to the environment knobs (cf. Katla et al. 2023, Fig. 2B-E)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    cfg = SimConfig()
    env = Environment()
    wz, woz = cfg.species
    drive = env.photon_drive()
    '''
    print(f"baseline photon drive : {drive:.3f}")
    print(f"R* for {wz.name:20s}: {wz.r_star(drive):.4f}")
    print(f"R* for {woz.name:20s}: {woz.r_star(drive):.4f}")
    print("lower R* wins the shared resource\n")

    mixed = simulate(env, cfg, n_init=(cfg.n0 / 2, cfg.n0 / 2))
    n_mix = cfg.n0 / 2
    print(f"final WZ  : {mixed['wz'][-1]:10.0f}  (started {n_mix:.0f})")
    print(f"final WOZ : {mixed['woz'][-1]:10.0f}  (started {n_mix:.0f}, "
          f"peaked {mixed['woz'].max():.0f} at t={mixed['t'][mixed['woz'].argmax()]:.0f} s)")
    print(f"final S   : {mixed['s'][-1]:.4f}")

    figure_competition(env, cfg, "protocell_competition.png")
    figure_environment_sweeps(cfg, "protocell_env_sweeps.png")
    print("\nwrote protocell_competition.png and protocell_env_sweeps.png")
    '''
    print("="*50 + "OBJECTS ANALYSIS" + "="*50)
    env = Environment()
    
    print(env)
    
    print(f"available wavelengths (nm): {env.wavelength_grid()}")
    
    

if __name__ == "__main__":
    main()
