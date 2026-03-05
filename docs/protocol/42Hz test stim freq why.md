md
# Optimal Test Frequency Selection: 42 Hz

To minimize spectral leakage from a 50 Hz power line and its harmonics (100 Hz, 150 Hz, 200 Hz), the test frequency $f_{test}$ and its own harmonics must maintain the largest possible distance from the set $\{50, 100, 150, 200\}$.

## Mathematical Analysis of 42 Hz

When using **42 Hz** as the fundamental test frequency, the resulting harmonic series provides a robust buffer against all 50 Hz interference points up to 200 Hz.


| Harmonic | Frequency | Nearest 50 Hz Multiple | Absolute Delta (Distance) |
| :--- | :--- | :--- | :--- |
| **1st (Fundamental)** | **42 Hz** | 50 Hz | **8 Hz** |
| **2nd** | **84 Hz** | 100 Hz | **16 Hz** |
| **3rd** | **126 Hz** | 150 Hz | **24 Hz** |
| **4th** | **168 Hz** | 150 Hz | **18 Hz** |
| **5th** | **210 Hz** | 200 Hz | **10 Hz** |

### Key Advantages:

1. **Maximized Minimum Distance:** Within the critical 0–200 Hz range, the "worst-case" proximity to any 50 Hz harmonic is **8 Hz**. This is superior to other integers like 41 Hz (which gets within 5 Hz of the 200 Hz line) or 38 Hz (which gets within 2 Hz of the 150 Hz line).
2. **Spectral Leakage Suppression:** Spectral leakage occurs when energy from a frequency "bleeds" into adjacent bins. By ensuring a minimum gap of 8 Hz, you provide maximum clearance for the main lobes of your test signal, even when using windows with wider main lobes (like Blackman-Harris).
3. **Integer Stability:** As an integer, 42 Hz is easily reproducible in digital synthesis without requiring complex fractional clock dividers, ensuring the frequency remains stable relative to the sampling rate.

## Comparison with Nearby Candidates

*   **41 Hz:** Fails at the 5th harmonic (205 Hz vs 200 Hz), leaving only a **5 Hz** margin.
*   **43 Hz:** Fails at the 3rd and 4th harmonics (129 Hz and 172 Hz), leaving only a **7 Hz** margin.
*   **42 Hz:** Maintains a **strictly $\ge$ 8 Hz** margin throughout the entire relevant spectrum.

**Conclusion:** For a system constrained to integer values, **42 Hz** is the mathematically optimal choice to isolate a test signal and its harmonics from 50 Hz power line interference.