import { ButtonHTMLAttributes } from "react";
import styles from "./Button.module.css";

// component-btn (experience-design.md §4A) — the one button control every
// AUTH screen uses. States: default, hover, focus, active, disabled,
// loading (spinner replaces label, button keeps its width — no layout shift).
type Variant = "primary" | "secondary" | "destructive" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
}

export function Button({
  variant = "primary",
  loading = false,
  disabled,
  children,
  className,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={[styles.btn, styles[variant], className].filter(Boolean).join(" ")}
      disabled={disabled || loading}
      aria-busy={loading}
      {...rest}
    >
      {loading ? <span className={styles.spinner} aria-hidden="true" /> : children}
    </button>
  );
}
