import { Queue } from "bullmq";
import { Worker } from "bullmq";
import { QueueEvents } from "bullmq";
import IORedis from "ioredis";

import { JOBS_MAPPING } from "./jobs";

const connection = new IORedis(6379, "localhost", {
  maxRetriesPerRequest: null,
});

const queueEvents = new QueueEvents("Paint");

queueEvents.on("completed", ({ jobId }) => {
  console.log(`done ${jobId}`);
});

queueEvents.on(
  "failed",
  ({ jobId, failedReason }: { jobId: string; failedReason: string }) => {
    console.error(`error on ${jobId}: `, failedReason);
  },
);

new Queue("etranslation");

new Worker(
  "etranslation",
  async (job) => {
    const handler = JOBS_MAPPING[job.name];
    if (handler) {
      await handler(job.data);
    }
  },
  { connection },
);
