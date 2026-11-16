import { useState } from "react";
import { ComboBox, Input, ListBox, ListBoxItem, Popover, Label } from "react-aria-components";
import * as Dialog from "@radix-ui/react-dialog";

const itens = ["Sargento Fahur", "Tabata Amaral", "Nikolas Ferreira", "Erika Hilton", "Arthur Lira"];

export default function Pecas() {
  const [escolhido, setEscolhido] = useState<string>("");
  return (
    <div>
      <ComboBox onSelectionChange={(k) => setEscolhido(String(k ?? ""))}>
        <Label>Buscar deputado</Label>
        <Input data-testid="busca" />
        <Popover>
          <ListBox>
            {itens.map((i) => (
              <ListBoxItem key={i} id={i}>{i}</ListBoxItem>
            ))}
          </ListBox>
        </Popover>
      </ComboBox>
      <p data-testid="escolhido">escolhido: {escolhido}</p>
      <Dialog.Root>
        <Dialog.Trigger data-testid="abrir">Como calculamos</Dialog.Trigger>
        <Dialog.Portal>
          <Dialog.Content data-testid="dialogo">
            <Dialog.Title>Metodologia</Dialog.Title>
            <Dialog.Description>k de n votações</Dialog.Description>
            <Dialog.Close data-testid="fechar">Fechar</Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
