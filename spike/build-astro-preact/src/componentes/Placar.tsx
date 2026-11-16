import { useState } from "preact/hooks";

type Linha = { eixo: string; k_pos: number; k_neg: number; n: number };

// H3.6: o lado fica só no estado do componente; nenhuma requisição, nada guardado.
export default function Placar({ placar }: { placar: Linha[] }) {
  const [lado, setLado] = useState<Record<string, "pos" | "neg" | undefined>>({});
  return (
    <ul>
      {placar.map((l) => {
        const escolhido = lado[l.eixo];
        const k = escolhido === "pos" ? l.k_pos : escolhido === "neg" ? l.k_neg : undefined;
        return (
          <li key={l.eixo}>
            {l.eixo}:{" "}
            <button onClick={() => setLado({ ...lado, [l.eixo]: "pos" })}>a favor</button>
            <button onClick={() => setLado({ ...lado, [l.eixo]: "neg" })}>contra</button>{" "}
            {k === undefined ? `votou ${l.k_pos} e ${l.k_neg}` : `votou na sua direção em ${k} de ${l.n}`}
          </li>
        );
      })}
    </ul>
  );
}
