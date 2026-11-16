import { readFileSync } from "node:fs";
import Placar from "../../../componentes/Placar.jsx";

export const dynamicParams = false;

export function generateStaticParams() {
  return JSON.parse(readFileSync("dados/indice.json", "utf-8")).map((id) => ({ id }));
}

function ler(id) {
  return JSON.parse(readFileSync(`dados/deputados/${id}.json`, "utf-8"));
}

export async function generateMetadata({ params }) {
  const d = ler((await params).id);
  return { title: `${d.nome} (${d.partido}-${d.uf})`, openGraph: { title: `${d.nome} (${d.partido}-${d.uf}), 57ª legislatura` } };
}

export default async function Page({ params }) {
  const d = ler((await params).id);
  return (
    <main>
      <h1>{d.nome}</h1>
      <Placar placar={d.placar} />
      <table>
        <tbody>
          {d.votos.map((v) => (
            <tr key={v.votacao_id}>
              <td>{v.data}</td><td>{v.rotulo}</td><td>{v.resumo}</td><td>{v.voto}</td><td>{v.bancada} {v.orientacao}</td><td>{v.colegas.join("/")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
