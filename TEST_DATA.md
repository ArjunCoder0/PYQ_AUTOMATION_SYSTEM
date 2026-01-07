# Sample Test Data for PYQ System

This directory contains sample PDF filenames for testing the ZIP processor.

## Valid B.Tech/B.E Filenames

These should be ACCEPTED by the system:

1. `B.Tech_CSE_III_Sem_BSC301_Data_Structures.pdf`
2. `B.Tech_IT_V_Semester_PCC501_Database_Management_Systems.pdf`
3. `B.E._ME_VII_ESC701_Thermodynamics.pdf`
4. `B.E_EE_II_HSMC201_Engineering_Mathematics.pdf`
5. `Model_Curriculum_ECE_IV_PCC401_Digital_Electronics.pdf`
6. `B.Tech_CE_VI_MC601_Environmental_Engineering.pdf`
7. `B.Tech_CSE_VIII_OEC801_Machine_Learning.pdf`
8. `B.E._IT_I_BSC101_Programming_in_C.pdf`

## Invalid Filenames (Should be REJECTED)

These should be IGNORED by the system:

1. `B.Sc_Physics_III_Sem_PHY301_Quantum_Mechanics.pdf` (Not B.Tech/B.E)
2. `BCA_II_Sem_CS201_Data_Structures.pdf` (Not B.Tech/B.E)
3. `M.Tech_CSE_I_Sem_Advanced_Algorithms.pdf` (Not B.Tech/B.E)
4. `B.Pharm_IV_Sem_Pharmacology.pdf` (Not B.Tech/B.E)
5. `B.Tech_CSE_Random_Document.pdf` (Missing subject code)
6. `Engineering_Notes.pdf` (Invalid format)

## Testing Instructions

1. Create empty PDF files with these names (or use actual PDFs)
2. Create a ZIP file containing these PDFs
3. Upload via admin panel
4. Verify that only valid B.Tech/B.E papers are processed
5. Check that metadata is correctly extracted

## Expected Results

- **Total PDFs in ZIP**: 14
- **Valid Engineering Papers**: 8
- **Rejected Papers**: 6
- **Success Rate**: 57% (8/14)
