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

AMENDMENT A2 s6 -- WINNER'S CURSE. Added BEFORE any ESNQ development number exists.

    Authorization may NOT use the raw development point estimate mu_hat_dev. A development mean is
    itself noisy, and a noisy estimate that happened to land high would manufacture its own
    authorization -- the pool would be spent precisely when the estimate was luckiest. Use instead
    the CONSERVATIVE CLAIM, a one-sided 90 % lower confidence bound on the development mean:

        mu_claim = max(0, mu_hat_dev - 1.2815515655 * SE_dev)          SE_dev SESSION-CLUSTERED

    Blind spend requires ALL SEVEN of:
        1 every development gate passes          5 PRIMARY economics survive stress
        2 the ES-pairing mechanism null passes   6 mu_claim > 0
        3 causality gates pass                   7 power at true mean = mu_claim  >=  0.80
        4 independent streaming parity passes
    This lower-bound rule may NOT be weakened after seeing development results.
"""
from __future__ import annotations

import math
import sys

SIGMA_PROXY = 5250.81          # frozen consumed-session sd, declared in Amendment A1
N_BLIND = 15
ALPHA_1SIDED = 0.05
MIN_POWER_VS_ZERO = 0.80
Z_90_ONE_SIDED = 1.2815515655          # A2 s6: one-sided 90 % lower bound
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


def mu_claim(mu_hat_dev: float, se_dev: float) -> float:
    """A2 s6. The CONSERVATIVE claim the blind pool must be powered against.

    se_dev MUST be the session-clustered standard error of the development mean -- never a
    decision-level SE over ~331 x 44 rows, which would understate it by an order of magnitude and
    make every claim look authorizable.
    """
    return max(0.0, mu_hat_dev - Z_90_ONE_SIDED * se_dev)


def authorize(mu_hat_dev: float, se_dev: float, *, gates_pass: bool, mechanism_null_pass: bool,
              causality_pass: bool, parity_pass: bool, stress_pass: bool) -> dict:
    """The full seven-condition gate. Returns the decision and every input to it."""
    mc = mu_claim(mu_hat_dev, se_dev)
    pw = power_vs_zero(mc)
    conds = {"1_development_gates": bool(gates_pass),
             "2_es_pairing_mechanism_null": bool(mechanism_null_pass),
             "3_causality": bool(causality_pass),
             "4_independent_parity": bool(parity_pass),
             "5_stress_economics": bool(stress_pass),
             "6_mu_claim_positive": bool(mc > 0),
             "7_blind_power_ge_80pct": bool(pw >= MIN_POWER_VS_ZERO)}
    ok = all(conds.values())
    return {"mu_hat_dev": mu_hat_dev, "se_dev_session_clustered": se_dev,
            "mu_claim_90pct_lcb": mc, "power_at_mu_claim": pw,
            "conditions": conds, "decision": "AUTHORIZED" if ok else "WITHHELD",
            "status": ("BLIND SPEND AUTHORIZED" if ok else
                       "DEVELOPMENT-SUPPORTED / BLIND-UNDERPOWERED / BLIND UNSPENT")}


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
    print("")
    print("=" * 96)
    print("=== A2 s6 WINNER'S-CURSE HARDENING -- authorization uses mu_claim, NOT mu_hat_dev")
    print("=" * 96)
    print("    mu_claim = max(0, mu_hat_dev - 1.2815515655 * SE_dev)   SE_dev SESSION-CLUSTERED")
    print(f"    development n = 44, so SE_dev = sigma/sqrt(44) = ${SIGMA_PROXY/44**0.5:,.2f} if the")
    print("    development sd matches the proxy (the actual SE will come from the 44 sessions).")
    print("")
    print(f"    {'mu_hat_dev':>12} {'SE_dev':>10} {'mu_claim':>12} {'power@claim':>12}  {'AUTHORIZE?':>12}")
    se_d = SIGMA_PROXY / 44 ** 0.5
    for mh in (1000, 2000, 3371, 4000, 5000, 6000, 8000, 10000):
        mc = mu_claim(float(mh), se_d)
        print(f"    {mh:>12,} {se_d:>10,.0f} {mc:>12,.0f} {power_vs_zero(mc):>12.3f}  "
              f"{'YES' if power_vs_zero(mc) >= MIN_POWER_VS_ZERO else 'NO - UNSPENT':>12}")
    lo = 3371 + Z_90_ONE_SIDED * se_d
    print("")
    print(f"    >>> WITH THE CONSERVATIVE CLAIM, mu_hat_dev must reach ~${lo:,.0f}/session")
    print(f"    >>> (vs ${3371:,.0f} using the raw point estimate) - about "
          f"{lo/246:.0f}x the incumbent yardstick.")
    print("    >>> Stated plainly: BLIND UNSPENT is now the overwhelmingly likely outcome, and")
    print("    >>> that is the intended behaviour. The pool is protected from a lucky estimate.")


if __name__ == "__main__":
    table()
    sys.exit(0)
