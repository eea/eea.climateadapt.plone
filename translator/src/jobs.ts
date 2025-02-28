import type { CallETranslation, TypeJobsMapping } from "./types";

const call_plone_for_etranslation = async (data: CallETranslation) => {
  // TODO: reimplement the call here directly
  const obj_path = `${data.obj_url}?serial_id=${data.serial_id}&language=${data.language}`;

  // here we call plone view which calls eTranslation with the necessary info
  console.log(`Calling eTranslation for ${obj_path}`);
};

export const JOBS_MAPPING: TypeJobsMapping = {
  call_etranslation: call_plone_for_etranslation,
};
