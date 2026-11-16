import * as Dialog from "@radix-ui/react-dialog";

export default function SoRadix() {
  return (
    <Dialog.Root>
      <Dialog.Trigger>abrir</Dialog.Trigger>
      <Dialog.Portal><Dialog.Content><Dialog.Title>t</Dialog.Title></Dialog.Content></Dialog.Portal>
    </Dialog.Root>
  );
}
