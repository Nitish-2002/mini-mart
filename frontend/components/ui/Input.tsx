import { InputHTMLAttributes, useId } from "react";
import styles from "./Input.module.css";

// component-input (experience-design.md §4A) — the one text/email input
// control, reused by every form field across all three roles. States:
// default, focus, error (announced via aria-live on the helper text, never
// color alone — constraint-a11y), disabled.
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helperText?: string;
}

export function Input({ label, error, helperText, id, className, ...rest }: InputProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;

  return (
    <label className={styles.field} htmlFor={inputId}>
      <span className={styles.label}>{label}</span>
      <input
        id={inputId}
        className={[styles.input, error ? styles.error : "", className].filter(Boolean).join(" ")}
        aria-invalid={Boolean(error)}
        aria-describedby={error || helperText ? `${inputId}-helper` : undefined}
        {...rest}
      />
      {(error || helperText) && (
        <span
          id={`${inputId}-helper`}
          className={[styles.helper, error ? styles.error : ""].filter(Boolean).join(" ")}
          aria-live="polite"
        >
          {error ?? helperText}
        </span>
      )}
    </label>
  );
}
