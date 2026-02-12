"""
=====================================================================================
REINSURANCE RISK ENGINE — MONTE CARLO SIMULATION
Author: Jyoti Nayak (Tech Founder — Financial Intelligence / Risk Systems)

This program demonstrates how a real-world insurance / reinsurance risk engine works.

It models:

• Insurance portfolio risk
• Claim frequency and severity
• Reinsurance excess-of-loss structure
• Monte Carlo stochastic simulation
• Tail risk metrics (VaR / TVaR)
• Economic value of reinsurance
• Inflation stress testing

This type of engine is the foundation of:

• Insurance pricing engines
• Risk capital estimation
• Solvency modeling (Solvency II / IFRS17 style thinking)
• Reinsurance optimization
• Financial intelligence & enterprise risk platforms

The goal is to show how modern financial / insurance risk systems are built
using probability, statistics, and simulation.

=====================================================================================
"""

import numpy as np


# =============================================================================
# CONFIGURATION — PORTFOLIO + ECONOMIC ASSUMPTIONS
# =============================================================================

# Number of Monte Carlo simulations (higher = more accurate risk estimate)
N_SIM = 100000

# Number of policies in the insurance portfolio
N_POLICIES = 200

# Probability a policy generates a claim in a year (frequency model)
CLAIM_PROB = 0.20

# Reinsurance retention levels (Excess of Loss structure)
# Insurer pays up to R, reinsurer pays above R
RETENTIONS = [25, 30]

# Reinsurance premiums charged by reinsurer
PREMIUMS = {25: 48.5, 30: 38.2}

# Claim severity distribution assumptions (mean and volatility)
MEAN = 9.070
STD = 10.132


# =============================================================================
# CONVERT MEAN / STD → LOGNORMAL PARAMETERS
# =============================================================================
"""
Insurance claim sizes are typically heavy-tailed (few very large losses).
Lognormal distribution is commonly used to model such skewed financial risks.

We convert business inputs (mean & std) → lognormal parameters (mu, sigma)
used internally by the simulation engine.
"""
def lognormal_params(mean, std):
    sigma2 = np.log(1 + (std**2 / mean**2))
    sigma = np.sqrt(sigma2)
    mu = np.log(mean) - sigma2 / 2
    return mu, sigma


# =============================================================================
# MONTE CARLO RISK ENGINE
# =============================================================================
"""
This is the core of the simulation-based risk engine.

Each simulation represents one possible "future year" of insurance experience.

Steps per simulation:

1. Simulate how many claims occur (frequency risk)
2. Simulate claim sizes (severity risk)
3. Apply reinsurance contract
4. Calculate ceded loss to reinsurer
5. Repeat thousands of times to build risk distribution

From the simulated loss distribution we compute:

• Mean Loss (Expected Cost)
• Risk (Volatility)
• Value at Risk (99%) → Extreme loss threshold
• TVaR (Tail Risk) → Average loss beyond VaR
• Probability reinsurer pays
• Value for money of reinsurance

This is how real enterprise risk engines evaluate insurance structures.
"""
def run_engine(mean, std, title):

    print("\n==========================")
    print(title)
    print("==========================")

    mu, sigma = lognormal_params(mean, std)

    # Evaluate each reinsurance retention option
    for R in RETENTIONS:

        portfolio_losses = []
        reinsurer_hits = 0
        total_claims = 0

        # Monte Carlo Simulation Loop
        for _ in range(N_SIM):

            # Step 1 — Claim frequency simulation
            claims = np.random.binomial(1, CLAIM_PROB, N_POLICIES)
            n_claims = claims.sum()

            ceded_total = 0

            if n_claims > 0:

                # Step 2 — Claim severity simulation
                sizes = np.random.lognormal(mu, sigma, n_claims)

                # Step 3 — Apply reinsurance structure
                # Reinsurer pays only amount ABOVE retention
                ceded = np.maximum(0, sizes - R)
                ceded_total = ceded.sum()

                # Track how often reinsurer is triggered
                reinsurer_hits += np.sum(sizes > R)
                total_claims += n_claims

            # Record portfolio loss for this simulation year
            portfolio_losses.append(ceded_total)

        losses = np.array(portfolio_losses)

        # =============================================================================
        # RISK METRICS — ENTERPRISE RISK ANALYTICS
        # =============================================================================

        # Expected ceded loss (pricing benchmark)
        mean_loss = losses.mean()

        # Risk / volatility
        std_loss = losses.std()

        # Value-at-Risk (Extreme percentile)
        var_99 = np.percentile(losses, 99)

        # Tail Value-at-Risk (Average of worst 1% outcomes)
        tvar_99 = losses[losses >= var_99].mean()

        # Probability reinsurer pays
        prob_reinsurer = reinsurer_hits / total_claims

        # Economic value of reinsurance
        value_for_money = mean_loss / PREMIUMS[R]

        # =============================================================================
        # REPORT OUTPUT
        # =============================================================================

        print(f"\nRetention {R}")
        print("Expected Ceded Loss:", mean_loss)
        print("Risk (Std Dev):", std_loss)
        print("VaR 99% (Extreme Loss):", var_99)
        print("TVaR 99% (Tail Risk):", tvar_99)
        print("P(Reinsurer Pays):", prob_reinsurer)
        print("Value for Money:", value_for_money)


# =============================================================================
# CURRENT YEAR — BASE RISK PROFILE
# =============================================================================
run_engine(MEAN, STD, "Current Year")


# =============================================================================
# INFLATION SCENARIO — STRESS TESTING
# =============================================================================
"""
Real financial risk engines always simulate future stress conditions.

Here we model claim inflation (+8%) to see how reinsurance economics change.

This demonstrates:
• Forward risk projection
• Stress testing
• Risk sensitivity analysis
• Capital planning capability
"""
run_engine(MEAN * 1.08, STD * 1.08, "Next Year with Inflation")
