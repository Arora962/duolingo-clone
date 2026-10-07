import { Button3D } from "~/components/ui/Button3D";
import { Modal } from "~/components/ui/Modal";

type Props = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
};

export function ConfirmModal({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onCancel,
  onConfirm,
}: Props) {
  return (
    <Modal open={open} title={title} onClose={onCancel} widthClassName="max-w-sm">
      <p className="text-sm font-extrabold leading-6 text-[var(--color-text-muted)]">
        {description}
      </p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <Button3D tone="neutral" fullWidth onClick={onCancel}>
          {cancelLabel}
        </Button3D>
        <Button3D tone="red" fullWidth onClick={onConfirm}>
          {confirmLabel}
        </Button3D>
      </div>
    </Modal>
  );
}
