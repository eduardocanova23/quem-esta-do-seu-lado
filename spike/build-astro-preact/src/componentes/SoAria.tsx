import { ComboBox, Input, ListBox, ListBoxItem, Popover, Label } from "react-aria-components";

export default function SoAria() {
  return (
    <ComboBox>
      <Label>Buscar</Label>
      <Input />
      <Popover><ListBox><ListBoxItem id="a">a</ListBoxItem></ListBox></Popover>
    </ComboBox>
  );
}
