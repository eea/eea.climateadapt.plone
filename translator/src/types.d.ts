export type AsyncFunction = (...args: any[]) => Promise<unknown>;

export type TypeJobsMapping = {
  [key: string]: AsyncFunction;
};

export type CallETranslation = {
  obj_url: string;
  html: string;
  serial_id: number;
};
