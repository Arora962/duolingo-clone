import { Modal } from "~/components/ui/Modal";
import { Button3D } from "~/components/ui/Button3D";
import { Icon } from "~/components/ui/Icons";

type ComingSoonModalProps = {
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
};

export function ComingSoonModal({
  open,
  title,
  description = "This part of the learning experience is coming soon.",
  onClose,
}: ComingSoonModalProps) {
  return (
    <Modal
      open={open}
      title={title}
      onClose={onClose}
      widthClassName="max-w-sm"
    >
      <div className="flex flex-col items-center text-center">
        <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-blue-50 text-macaw dark:bg-[#143b4e]">
          <Icon name="sparkle" size={42} strokeWidth={2} />
        </div>

        <p className="text-base leading-6 text-[var(--color-text-muted)]">
          {description}
        </p>

        <Button3D tone="blue" fullWidth className="mt-6" onClick={onClose}>
          Got it
        </Button3D>
      </div>
    </Modal>
  );
}
