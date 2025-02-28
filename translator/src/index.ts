import { Queue } from "bullmq";
import { Worker } from "bullmq";
import { QueueEvents } from "bullmq";
import IORedis from "ioredis";

const connection = new IORedis(6379, "localhost", {
  maxRetriesPerRequest: null,
});

const queue = new Queue("Paint");

queue.add("cars", { color: "blue" });

const paintCar = async (color: string) => {
  console.log(`Painting ${color}`);
};

const queueEvents = new QueueEvents("Paint");

queueEvents.on("completed", ({ jobId }) => {
  console.log("done painting");
});

queueEvents.on(
  "failed",
  ({ jobId, failedReason }: { jobId: string; failedReason: string }) => {
    console.error("error painting", failedReason);
  },
);

const worker = new Worker(
  "Paint",
  async (job) => {
    if (job.name === "cars") {
      await paintCar(job.data.color);
    }
  },
  { connection },
);
