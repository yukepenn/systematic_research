"""blind_spend_power.py -- the PREDECLARED blind-spend admissibility formula (Amendment A1 s7).

COMMITTED BEFORE ANY ESNQ DEVELOPMENT RESULT EXISTS. This file's numbers are a function of a
development effect size mu_dev that has not been measured yet. Committing it now is the whole
point: once mu_dev is known, the authorization threshold cannot be reverse-engineered to permit
whatever was observed.

THE PROBLEM IT SOLVES. The 15-session blind pool is FALSIFIER-GRADE:
    session sd proxy   $5,250.81   (frozen, from the 48 already-consumed BBO sessions)
    n = 15  ->  SE     $1,355.87
    MDE(80%)           $3,372/session
A modest development effect CANNOT be adjudicated by spending it. Spending the pool on a claim it
cannot falsify destroys an irreversible asset and learns nothing.

    PASSING EVERY DEVELOPMENT GATE IS NECESSARY AND NOT SUFFICIENT.

DECLARED NOW, before any ESNQ number exists:
    VARIANCE PROXY   sigma = $5,250.81/session, the frozen consumed-session sd. Not re-selected
                     after seeing ESNQ results, and not replaced by an ESNQ-derived sd.
    MIN POWER        0.80 to reject a collapse to zero, at one-sided alpha = 0.05.
    If power < 0.80 the verdict is DEVELOPMENT-SUPPORTED / BLIND-UNDERPOWERED / BLIND UNSPENT.
"""
from __future__ import annotations

import math
import sys

SIGMA_PROXY = 5250.81          # frozen consumed-session sd, declared in Amendment A1
N_BLIND = 15
ALPHA_1SIDED = 0.05
MIN_POWER_VS_ZERO = 0.80
INCUMBENT_PER_SESSION = 246.0  # weak materiality yardstick: P1/PCT ~$1,230/wk over 5 sessions
Z_ALPHA = 1.6448536269514722   # Phi^-1(0.95)


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def se_blind(sigma: float = SIGMA_PROXY, n: int = N_BLIND) -> float:
    return sigma / math.sqrt(n)


def power_vs_zero(mu_dev: float, sigma: float = SIGMA_PROXY, n: int = N_BLIND) -> float:
    """Power of a one-sided test of H0: mu_blind <= 0 when the truth is mu_blind = mu_dev.

    'Can the pool detect that the development-sized claim is REAL?' If mu_dev <= 0 this is not a
    meaningful question and the function returns 0.
    """
    if mu_dev <= 0:
        return 0.0
    return _phi(mu_dev / se_blind(sigma, n) - Z_ALPHA)


def power_vs_collapse(mu_dev: float, mu_true: float = 0.0, sigma: float = SIGMA_PROXY,
                      n: int = N_BLIND) -> float:
    """Power to REJECT the claim mu = mu_dev when the truth is mu_true.

    This is the falsification direction and it is the one that matters for this pool: a one-sided
    test of H0: mu >= mu_dev against the truth mu_true < mu_dev.
    """
    if mu_dev <= mu_true:
        return 0.0
    return _phi((mu_dev - mu_true) / se_blind(sigma, n) - Z_ALPHA)


def expected_information_gain(mu_dev: float) -> dict:
    """The three numbers Amendment A1 s7 requires, reported as a function of mu_dev."""
    se = se_blind()
    return {
        "mu_dev_per_session": mu_dev,
        "se_blind_per_session": se,
        "mde_80_per_session": (Z_ALPHA + 0.8416212335729143) * se,
        "power_vs_zero": power_vs_zero(mu_dev),
        "power_to_reject_collapse_to_zero": power_vs_collapse(mu_dev, 0.0),
        "power_to_reject_sign_reversal": power_vs_collapse(mu_dev, -mu_dev),
        "power_to_reject_economically_null": power_vs_collapse(mu_dev, INCUMBENT_PER_SESSION),
        "min_power_required": MIN_POWER_VS_ZERO,
        "authorized": power_vs_zero(mu_dev) >= MIN_POWER_VS_ZERO,
    }


def table():
    se = se_blind()
    print("=" * 96)
    print("=== BLIND-SPEND ADMISSIBILITY -- PREDECLARED, before any ESNQ result exists")
    print("=" * 96)
    print(f"    sigma proxy (frozen)   ${SIGMA_PROXY:,.2f}/session")
    print(f"    n blind                {N_BLIND}")
    print(f"    SE_blind               ${se:,.2f}/session")
    print(f"    MDE(80% power)         ${(Z_ALPHA + 0.8416212335729143) * se:,.2f}/session")
    print(f"    MIN POWER TO AUTHORIZE {MIN_POWER_VS_ZERO:.2f}  (reject a collapse to zero)")
    print("")
    print(f"    {'mu_dev $/session':>18} {'power vs 0':>11} {'vs sign-rev':>12} "
          f"{'vs $246':>9}   {'AUTHORIZE?':>11}")
    for mu in (246, 500, 1000, 1500, 1969, 2500, 3000, 3372, 4000, 5125):
        g = expected_information_gain(float(mu))
        print(f"    {mu:>18,} {g['power_vs_zero']:>11.3f} "
              f"{g['power_to_reject_sign_reversal']:>12.3f} "
              f"{g['power_to_reject_economically_null']:>9.3f}   "
              f"{'YES' if g['authorized'] else 'NO -- UNSPENT':>11}")
    thr = (Z_ALPHA + 0.8416212335729143) * se
    print("")
    print(f"    >>> THE AUTHORIZATION THRESHOLD IS mu_dev >= ${thr:,.0f}/session.")
    print(f"    >>> That is {thr / INCUMBENT_PER_SESSION:.1f}x the incumbent per-session yardstick.")
    print("    >>> A development effect below it leaves the pool UNSPENT and routes the object to")
    print("    >>> prospective accumulation instead. This is declared BEFORE mu_dev is measured.")


if __name__ == "__main__":
    table()
    sys.exit(0)
