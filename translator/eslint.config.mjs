import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";

/** @type {import('eslint').Linter.Config[]} */
const config = [
  { files: ["**/*.{js,mjs,cjs,ts}"] },
  { languageOptions: { globals: globals.browser } },
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
];

config.plugins = [...(config.plugins || []), "prettier"];
config.push({
  name: "typescript-eslint/custom-rules",
  rules: {
    "@typescript-eslint/no-explicit-any": "off",
  },
});
config.rules = { ...config.rules, "@typescript-eslint/no-explicit-any": "off" };

export default config;
