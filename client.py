import aiohttp
import asyncio
import time
import logging

logging.basicConfig(filename='log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch(session, url, request_id, timeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            status = response.status
            if status != 200:
                logging.warning(f"Request {request_id}: Non-200 status code: {status}")
            else:
                logging.info(f"Request {request_id}: Success - Status code: {status}")
            return await response.text()
    except asyncio.TimeoutError:
        logging.error(f"Request {request_id}: Connection timeout after {timeout} seconds")
    except aiohttp.ClientConnectorError as e:
        logging.error(f"Request {request_id}: Connection error (server might be down): {str(e)}")
    except aiohttp.ServerDisconnectedError:
        logging.error(f"Request {request_id}: Server disconnected")
    except Exception as e:
        logging.error(f"Request {request_id}: Unexpected error: {str(e)}")
    return None

async def test_get(num_requests, timeout):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(fetch(session, "http://localhost:3030/json", i+1, timeout))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Completed {num_requests} requests in {total_time:.2f} seconds")
    logging.info(f"Average time per request: {total_time / num_requests:.4f} seconds")

    # Count successful, failed, and timed out requests
    successes = sum(1 for r in results if r is not None)
    failures = num_requests - successes
    timeouts = sum(1 for r in results if isinstance(r, asyncio.TimeoutError))
    logging.info(f"Successful requests: {successes}")
    logging.info(f"Failed requests: {failures}")
    logging.info(f"Timed out requests: {timeouts}")

async def main():
    num_requests = 10000
    timeout = 10  # timeout in seconds
    logging.info(f"Starting test with {num_requests} requests and {timeout} second timeout")
    await test_get(num_requests, timeout)

if __name__ == "__main__":
    asyncio.run(main())