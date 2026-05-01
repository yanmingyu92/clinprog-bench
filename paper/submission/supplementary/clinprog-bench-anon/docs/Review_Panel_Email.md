Subject: Action Required: ClinProg-Bench Expert Panel Review (Phase 2.2)

Hi Guanlong, Jason, and Xiyang,

Thank you for agreeing to serve on the expert reviewer panel for **ClinProg-Bench v0.1**.

We have generated the 250-task public benchmark and published it, but to fulfill our governance requirements, we must conduct a dual-reviewer human audit on a stratified random sample of 20 tasks to ensure clinical and technical soundness.

Our target is a **Cohen's kappa (κ) ≥ 0.8** agreement.

### Your Assignments

The 20-task review package has been attached to this email (`review_package.zip`). Inside, you will find 4 tasks from each of our 5 categories (T1–T5), complete with prompts, specifications, fixtures, and the generated gold-standard outputs.

Your specific assignments are:
* **Guanlong (R01):** T1 (Code Gen), T3 (Spec Extract), T4 (Documentation)
* **Jason (R02):** T1 (Code Gen), T2 (Code Review), T4 (Documentation), T5 (Debugging)
* **Xiyang (R03):** T2 (Code Review), T3 (Spec Extract), T5 (Debugging)

*(This setup ensures every task is dual-reviewed).*

### Instructions

1. **Review:** For your assigned categories, review the task JSON and the corresponding `expected_output` files in the `gold/` folder.
2. **Evaluate:** For each task, record a binary (Pass/Fail) judgment based on whether the gold output accurately reflects the task specification and adheres to standard CDISC/industry programming guidelines.
3. **Log:** Use the attached `audit-log.md` file template to record your findings and notes.

Please return your completed logs by **2026-05-12**. If there are disagreements, we will schedule a brief reconciliation call to resolve them.

Thank you for ensuring the GxP and Pharma-grade rigor of this benchmark!

Best regards,

Anonymous Author
Project Manager, ClinProg-Bench
