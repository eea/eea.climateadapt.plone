export type AsyncFunction = (...args: any[]) => Promise<unknown>;

export type TypeJobsMapping = {
  [key: string]: AsyncFunction;
};

export type CallETranslation = {
  html: string;
  language: string;
  obj_url: string;
  serial_id: number;
};
