"use client";

import { ClipboardEvent, KeyboardEvent, useRef } from "react";
import styles from "./OtpInput.module.css";

// component-otp-input (experience-design.md §4A) — 6-box segmented code
// input. Auto-advances focus per digit, backspace moves focus back, pasting
// a full code fills all 6 boxes at once (decision-64). Error state flashes
// all 6 boxes, not color alone — the actual message (wrong vs expired vs
// generic) is the caller's own copy, announced by OtpVerifyScreen itself,
// not duplicated here.
const LENGTH = 6;

interface OtpInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: boolean;
  disabled?: boolean;
}

export function OtpInput({ value, onChange, error, disabled }: OtpInputProps) {
  const refs = useRef<Array<HTMLInputElement | null>>([]);

  const digits = value.padEnd(LENGTH, " ").split("").slice(0, LENGTH);

  function setDigit(index: number, digit: string) {
    const next = digits.slice();
    next[index] = digit;
    onChange(next.join("").trimEnd());
  }

  function handleChange(index: number, raw: string) {
    const digit = raw.replace(/\D/g, "").slice(-1);
    if (!digit) return;
    setDigit(index, digit);
    if (index < LENGTH - 1) {
      refs.current[index + 1]?.focus();
    }
  }

  function handleKeyDown(index: number, event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Backspace" && !digits[index]?.trim() && index > 0) {
      refs.current[index - 1]?.focus();
      setDigit(index - 1, "");
    }
  }

  function handlePaste(event: ClipboardEvent<HTMLInputElement>) {
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, LENGTH);
    if (!pasted) return;
    event.preventDefault();
    onChange(pasted);
    refs.current[Math.min(pasted.length, LENGTH - 1)]?.focus();
  }

  return (
    <div>
      <div className={styles.row} role="group" aria-label="6-digit verification code">
        {digits.map((digit, index) => (
          <input
            key={index}
            ref={(el) => {
              refs.current[index] = el;
            }}
            className={[styles.box, error ? styles.error : ""].filter(Boolean).join(" ")}
            inputMode="numeric"
            autoComplete={index === 0 ? "one-time-code" : "off"}
            maxLength={1}
            value={digit.trim()}
            disabled={disabled}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            onPaste={handlePaste}
            aria-label={`Digit ${index + 1} of ${LENGTH}`}
          />
        ))}
      </div>
    </div>
  );
}
