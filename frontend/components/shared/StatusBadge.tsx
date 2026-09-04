import styles from "./StatusBadge.module.css";

// dc-auth-001 (experience-design.md §4C) — color mapped to
// sm-auth-agent-status's four values. Source screen: ds-auth-006. Reused
// by CATALOG/ORDERS' own future admin screens showing agent status.
export type AgentStatus = "pending_approval" | "approved" | "deactivated" | "rejected";

const LABEL: Record<AgentStatus, string> = {
  pending_approval: "Pending approval",
  approved: "Approved",
  deactivated: "Deactivated",
  rejected: "Rejected",
};

const STYLE_KEY: Record<AgentStatus, string> = {
  pending_approval: "pending",
  approved: "approved",
  deactivated: "deactivated",
  rejected: "rejected",
};

export function StatusBadge({ status }: { status: AgentStatus }) {
  return (
    <span className={`${styles.badge} ${styles[STYLE_KEY[status]]}`}>
      <span className={styles.dot} aria-hidden="true" />
      {LABEL[status]}
    </span>
  );
}
