import { Button3D } from "~/components/ui/Button3D";
import { Modal } from "~/components/ui/Modal";

type ConfirmModalProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmModal({
  open,
  title,
  description,
  confirmLabel,
  cancelLabel = "Not now",
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  return (
    <Modal open={open} title={title} onClose={onCancel} widthClassName="max-w-sm">
      <p className="text-sm leading-6 text-[var(--color-text-muted)]">
        {description}
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <Button3D tone="neutral" fullWidth onClick={onCancel}>
          {cancelLabel}
        </Button3D>
        <Button3D tone="green" fullWidth onClick={onConfirm}>
          {confirmLabel}
        </Button3D>
      </div>
    </Modal>
  );
}
