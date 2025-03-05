import type {
  CallETranslation,
  SaveTranslation,
  TypeJobsMapping,
} from "./types";
import mockData from "./mock-data.json";

const base = "http://localhost:8080/cca";

function dataToForm(data) {
  const form = new FormData();
  Object.entries(data).forEach(([name, value]) => {
    form.append(name, value as any);
  });
  return form;
}

async function mockTranslationCallback(obj_path: string) {
  const form = dataToForm({ ...mockData, "external-reference": obj_path });
  const response = await fetch(`${base}/@@translate-callback`, {
    method: "POST",
    body: form,
  });
  const result = await response.text();
  return result;
}

async function call_plone_for_etranslation(data: CallETranslation) {
  // TODO: reimplement the call here directly
  const obj_path = `${data.obj_url}?serial_id=${data.serial_id}&language=${data.language}`;

  // here we call plone view which calls eTranslation with the necessary info
  console.log(`Calling eTranslation for ${obj_path}`);

  const form = dataToForm({
    html: data.html,
    target_lang: data.language,
    obj_path,
  });

  const response = await fetch(`${base}/@@call-etranslation`, {
    method: "POST",
    body: form,
    headers: {
      Authentication: process.env.TRANSLATION_AUTH_TOKEN || "hello1234",
    },
  });
  const result = await response.json();
  console.log("result", result);

  // mock implementation, we call Plone just like eTranslation would do
  await mockTranslationCallback(obj_path);
}

async function save_translation_to_plone(data: SaveTranslation) {
  const { obj_path, html } = data;
  const url = new URL(obj_path);
  const form = dataToForm({
    path: url.pathname,
    html,
    language: url.searchParams.get("language") || "missing",
    serial_id: url.searchParams.get("serial_id") || "missing",
  });

  const response = await fetch(`${base}/@@save-etranslation`, {
    method: "POST",
    body: form,
    headers: {
      Authentication: process.env.TRANSLATION_AUTH_TOKEN || "hello1234",
    },
  });
  const result = await response.json();
  console.log("save translation result", result);
}

export const JOBS_MAPPING: TypeJobsMapping = {
  call_etranslation: call_plone_for_etranslation,
  save_translated_html: save_translation_to_plone,
};
