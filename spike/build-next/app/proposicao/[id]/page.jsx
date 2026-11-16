import { readFileSync } from "node:fs";

export const dynamicParams = false;
const proposicoes = JSON.parse(readFileSync("dados/proposicoes.json", "utf-8"));
const porId = new Map(proposicoes.map((p) => [p.id, p]));

export function generateStaticParams() {
  return proposicoes.map((p) => ({ id: p.id }));
}

export async function generateMetadata({ params }) {
  return { title: porId.get((await params).id).rotulo };
}

export default async function Page({ params }) {
  const p = porId.get((await params).id);
  return (
    <main>
      <h1>{p.rotulo}</h1>
      <p>{p.resumo}</p>
      <p>{p.ementa}</p>
      <ul>{p.autores.map((a) => <li key={a}><a href={`/deputado/${a}/`}>{a}</a></li>)}</ul>
    </main>
  );
}
