# Patient Preparation & EEG Cap Setup Guide

This guide provides instructions for setting up the **Tenocom 32ch EEG Cap** and electrodes for data acquisition using the **FreeEEG32** system, based on the current hardware configuration (13/11).

---

## 1. Preparation Checklist
- [ ] Tenocom 32-channel EEG Cap (appropriate size for patient).
- [ ] Conductive EEG Gel/Paste.
- [ ] Preparation pads or alcohol swabs.
- [ ] Ear clips (for Linked Ears reference).
- [ ] Syringe and blunt needle (if using gel-based cap).
- [ ] Cotton swabs for skin preparation.

---

## 2. Electrode Placement (8-Channel Montage)

Apply gel and ensure low impedance for the following **8 active locations** according to the 10-20 system:

| Location | Hardware CH | Description |
| :--- | :--- | :--- |
| **T7** | CH 1 | Left Temporal |
| **C3** | CH 2 | Left Central |
| **T8** | CH 5 | Right Temporal |
| **FC4** | CH 6 | Right Fronto-Central |
| **FC3** | CH 9 | Left Fronto-Central |
| **C4** | CH 10 | Right Central |
| **CP3** | CH 13 | Left Centro-Parietal |
| **CP4** | CH 14 | Right Centro-Parietal |

---

## 3. Reference and Bias (Ground) Setup

Critical for signal quality and noise rejection:

*   **REFERENCE (REF): Linked Ears**
    *   Place ear clips on both the **Left and Right Earlobes**.
    *   Ensure these are connected to the system's Reference input.
*   **VCM_BIAS (GND): FPZ | FZ**
    *   Place the Ground/Bias electrode on the **forehead (FPZ)** or **midline frontal (FZ)**.
    *   This is essential for the system's Common Mode Rejection.

---

## 4. Diagnostic/Test Channels (System Check)

Two channels are reserved for system diagnostic monitoring and do **not** require patient attachment:
*   **CH 26 (x26):** Should be **shorted with a jumper** at the board (used for noise floor monitoring).
*   **CH 30 (x30):** Should be left **open / floating** (no wire attached).

---

## 5. Setup Procedure

1.  **Measure and Mark:** Measure the patient's head circumference and mark the CZ (vertex) point.
2.  **Cap Placement:** Fit the cap, ensuring CZ on the cap aligns with the vertex. Secure the chin strap.
3.  **Skin Prep:** Use a cotton swab and prep paste/alcohol at each active site (T7, C3, etc.) and the reference/bias sites (Ears, FPZ).
4.  **Gel Application:** 
    *   Insert gel into the electrode housing.
    *   Gently move the hair aside with the needle tip to ensure direct skin contact.
    *   Fill until the gel just touches the electrode sensor.
5.  **Reference/Bias:** Attach ear clips and the forehead ground electrode. These must have the best possible contact.
6.  **Impedance Check:** Open the **EEGlslviewer** and check the signal stability. All active channels should show a clean baseline without excessive 50/60Hz noise.

---

## 6. Troubleshooting
*   **High 50/60Hz Noise:** Check the GND (FPZ/FZ) connection first. Ensure it hasn't dried out.
*   **Flat Lines:** Check if the hardware channel matches the mapping (e.g., ensure wire 1 is actually in CH1).
*   **Drifting/DC Offset:** Usually caused by poor contact or sweat bridges between electrodes. Re-clean and re-gel the site.
