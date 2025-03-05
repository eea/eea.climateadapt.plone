import { JOBS_MAPPING } from "./jobs";
import { createBullBoard } from "@bull-board/api";
import { BullMQAdapter } from "@bull-board/api/bullMQAdapter";
import { FastifyAdapter } from "@bull-board/fastify";
import { Queue, Worker } from "bullmq";
import fastify from "fastify";
import IORedis from "ioredis";

const port = parseInt(process.env.PORT || "3000");

const connection = new IORedis({
  maxRetriesPerRequest: null,
  port: parseInt(process.env.REDIS_PORT || "6379"),
  host: process.env.REDIS_HOST || "0.0.0.0",
});

const sub = new IORedis({
  maxRetriesPerRequest: null,
  port: parseInt(process.env.REDIS_PORT || "6379"),
  host: process.env.REDIS_HOST || "0.0.0.0",
});

// console.log("connection", connection);

const createQueueMQ = (name: string) => new Queue(name, { connection });

function setupBullMQProcessor(queueName: string) {
  new Worker(
    queueName,
    async (job) => {
      const handler = JOBS_MAPPING[job.name];
      console.log(handler);
      if (handler) {
        await handler(job.data);
      }

      return { jobId: `This is the return value of job (${job.id})` };
    },
    { connection },
  );
}

function readQueuesFromEnv() {
  const qStr = process.env.BULL_QUEUE_NAMES_CSV || "etranslation";
  try {
    const qs = qStr.split(",");
    return qs.map((q) => q.trim());
  } catch (e) {
    console.error(e);
    return [];
  }
}

sub.subscribe("etranslation", (err, count) => {
  if (err) {
    // Just like other commands, subscribe() can fail for some reasons,
    // ex network issues.
    console.error("Failed to subscribe: %s", err.message);
  } else {
    // `count` represents the number of channels this client are currently subscribed to.
    console.log(
      `Subscribed successfully! This client is currently subscribed to ${count} channels.`,
    );
  }
});

sub.on("message", (channel, message) => {
  console.log(`Received ${message} from ${channel}`);
});

// There's also an event called 'messageBuffer', which is the same as 'message' except
// it returns buffers instead of strings.
// It's useful when the messages are binary data.
sub.on("messageBuffer", (channel, message) => {
  // Both `channel` and `message` are buffers.
  console.log(channel, message);
});

const run = async () => {
  const queues = readQueuesFromEnv().map((q) => createQueueMQ(q));

  queues.forEach((q) => {
    setupBullMQProcessor(q.name);
  });

  const app = fastify();

  const serverAdapter = new FastifyAdapter();

  createBullBoard({
    queues: queues.map((q) => new BullMQAdapter(q)),
    serverAdapter,
  });

  serverAdapter.setBasePath("/ui");
  app.register(serverAdapter.registerPlugin() as any, { prefix: "/ui" });

  app.get("/add", (req, reply) => {
    const opts = (req.query as any).opts || {};

    if (opts.delay) {
      opts.delay = +opts.delay * 1000; // delay must be a number
    }

    queues.forEach((queue) =>
      queue.add("Add", { title: (req.query as any).title }, opts),
    );

    reply.send({
      ok: true,
    });
  });

  app.get("/status", (req, reply) => {
    console.log(connection.status);
    reply.send({ status: connection.status });
  });

  await app.listen({ host: "0.0.0.0", port });

  console.log(`For the UI, open http://localhost:${port}/ui`);
  console.log(
    "Make sure Redis is configured in env variables. See .env.example",
  );
  console.log("To populate the queue, run:");
  console.log(`  curl http://localhost:${port}/add?title=Example`);
  console.log("To populate the queue with custom options (opts), run:");
  console.log(`  curl http://localhost:${port}/add?title=Test&opts[delay]=9`);
};

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
