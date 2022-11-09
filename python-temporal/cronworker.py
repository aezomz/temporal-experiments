import asyncio
import random
import string
import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

task_queue = "cron"
workflow_name = "say-hello-workflow"
activity_name = "say-hello-activity"
logging.basicConfig(level=logging.INFO)

@activity.defn(name=activity_name)
async def say_hello_activity(name: str) -> str:
    activity.logger.info("Running activity with parameter %s" % name)
    return f"Hello, {name}!"

@workflow.defn(name=workflow_name)
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> None:
        result = await workflow.execute_activity(
            say_hello_activity,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info("Result: %s", result)

async def main():
    # Create client to localhost on default namespace
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[GreetingWorkflow],
        activities=[say_hello_activity],
    )
    await worker.run()
    # await worker.run()
    # await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
