import { defineConfig } from "astro/config";
import preact from "@astrojs/preact";

export default defineConfig({
  output: "static",
  integrations: [preact({ compat: true })],
  // Sem isto o build carrega o React de verdade dentro das bibliotecas, e o preact-render-to-string quebra.
  vite: { ssr: { noExternal: [/react-aria/, /@react-aria/, /@react-stately/, /@radix-ui/, /@internationalized/] } },
});
