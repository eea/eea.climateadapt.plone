import type {
  CallETranslation,
  SaveTranslation,
  TypeJobsMapping,
} from "./types";
import mockData from "./mock-data.json";

const PORTAL_URL = process.env.PORTAL_URL || "http://localhost:8080/cca";

console.log("Portal URL: ", PORTAL_URL);

type Mapping = { [key: string]: any };

function dataToForm(data: Mapping) {
  const form = new FormData();
  Object.entries(data).forEach(([name, value]) => {
    form.append(name, value);
  });
  return form;
}

export async function mockTranslationCallback(obj_path: string) {
  const form = dataToForm({ ...mockData, "external-reference": obj_path });
  const response = await fetch(`${PORTAL_URL}/@@translate-callback`, {
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

  const response = await fetch(`${PORTAL_URL}/@@call-etranslation`, {
    method: "POST",
    body: form,
    headers: {
      Authentication: process.env.TRANSLATION_AUTH_TOKEN || "hello1234",
    },
  });
  const result = await response.json();
  console.log("Call ETranslation Result", result);

  if (result.error_type) {
    throw result.error_type;
  }

  return result;

  // mock implementation, we call Plone just like eTranslation would do
  // await mockTranslationCallback(obj_path);
}

async function save_translation_to_plone(data: SaveTranslation) {
  const { obj_path, html } = data;
  const url_path = `http://example.com${obj_path}`;
  console.log("url_path", url_path);
  const url = new URL(url_path);
  const form = dataToForm({
    path: url.pathname,
    html,
    language: url.searchParams.get("language") || "missing",
    serial_id: url.searchParams.get("serial_id") || "missing",
  });

  const response = await fetch(`${PORTAL_URL}/@@save-etranslation`, {
    method: "POST",
    body: form,
    headers: {
      Authentication: process.env.TRANSLATION_AUTH_TOKEN || "",
    },
  });
  const result = await response.json();
  console.log("Save translation result", result);

  if (result.error_type) {
    throw result.error_type;
  }
  return result;
}

export const JOBS_MAPPING: TypeJobsMapping = {
  call_etranslation: call_plone_for_etranslation,
  save_translated_html: save_translation_to_plone,
};
