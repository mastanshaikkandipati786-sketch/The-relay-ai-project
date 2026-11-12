
# The Relay: Research Paper Question-Answering Assistant

## 1. What I built and why

I built The Relay using Python and the Groq API.

It answers questions using information from three research papers:

- Attention Is All You Need (arXiv:1706.03762 v7)
- Moshi (arXiv:2410.00037 v1)
- Dynamic Chunking for End-to-End Hierarchical Sequence Modeling (arXiv:2507.07955 v2)

My project includes:
- PDF text extraction.
- BM25 search.
- Groq AI answer generation.
- Answer verification.
- A stand-in simulator.
- CSV experiment results and analysis.

## 2. The real service and my stand-in

I used the Groq API with the openai/gpt-oss-20b model.

The Groq documentation listed these free-plan limits:

- RPM: 1,000
- RPD: 500,000
- TPM: 250,000

During testing, Groq returned an error showing an effective limit of 8,000 TPM for my account.

### Table 1: Groq rate limits

| Limit | Free-plan documentation |
|---|---:|
| Requests per minute (RPM) | 1,000 |
| Requests per day (RPD) | 500,000 |
| Tokens per minute (TPM) | 250,000 |
| Tokens per day (TPD) | Not listed |
| Concurrent requests | Not listed |

I also created a stand-in simulator using Python.

It can simulate:
- Response delays.
- Rate limits.
- Random failures.
- Slow responses under heavy load.
- Streaming responses.

The simulator helps test different situations without repeatedly calling the real API. It does not perfectly represent Groq.

## 3. Results

### Table 2a: Latency by scenario (stand-in)

Only successful requests are included in these latency calculations.

| Scenario | Successful requests | Average (ms) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|---:|---:|
| Steady | 3 | 1309.08 | 1309.12 | 1309.66 | 1309.71 |
| Burst | 8 | 2246.81 | 2059.46 | 3634.30 | 3774.50 |
| Sustained overload | 6 | 2143.43 | 2059.54 | 3186.40 | 3286.37 |
| Half-minute limit | 5 | 1008.53 | 1008.68 | 1009.11 | 1009.13 |

### Table 2b: Outcomes by scenario (stand-in)

| Scenario | Successful | Rate-limited | Errors |
|---|---:|---:|---:|
| Steady | 3 | 0 | 0 |
| Burst | 8 | 2 | 2 |
| Sustained overload | 6 | 0 | 0 |
| Half-minute limit | 5 | 2 | 0 |
| Daily budget exhausted | 0 | 1 | 0 |

The daily budget exhausted result is a simulated pre-check, not an actual Groq daily quota error.

In my quality experiment, 7 answers were successfully generated and reviewed. These 7 answers were graded correct. The other 9 requests were rate-limited.

The successful real requests used different numbers of tokens. I did not calculate a reliable average tokens-per-answer value.

I did not calculate the cost per 1,000 answers because I did not have a verified cost figure for my free-plan usage. The actual token usage is recorded in results.csv.

## 4. Where the time goes

The real Groq requests had different response times.

The first-token time measures how long the user waits for the first part of the answer. The total time includes generating the complete answer.

The p50 value shows the middle response time. The p95 and p99 values show slower requests.

In my experiment, real Groq had an average latency of 1374.03 ms, while the stand-in had an average latency of 1809.32 ms.

For all recorded successful requests, the real Groq p50, p95 and p99 were 1067.70 ms, 2769.11 ms and 3299.78 ms.

The stand-in p50, p95 and p99 were 1309.47 ms, 3311.23 ms and 3704.93 ms.

These measurements are from my recorded requests, not a general performance guarantee.

## 5. When a limit is hit

During my experiment, real Groq had 9 rate-limited requests.

The stand-in had 5 rate-limited requests.

Groq reported an effective limit of 8,000 tokens per minute in an error message.

When a rate limit happens, the application should wait before trying again. Sending requests repeatedly can cause more failures.

The experiment showed that rate limits can reduce the number of successful answers.

## Retrieval: quality versus cost

I used BM25 retrieval to find relevant pages from the research papers.

I selected the top 3 passages for each question.

Using more passages can provide more information to the AI model, but it can also increase the number of input tokens.

Using fewer passages can reduce token usage, but important information may be missed.

### Table 3: Retrieval settings

| Setting | Value used | Purpose |
|---|---|---|
| Retrieval method | BM25 | Finds passages using matching words |
| Top-k | 3 | Selects the three highest-ranked passages |
| Title bonus | Enabled | Gives extra weight to matching paper titles |
| Exact phrase bonus | Enabled | Rewards exact phrase matches |
| Verifier threshold | 0.20 | Checks lexical overlap with the answer |
| Real experiment setting | BM25_top3 | Records the retrieval setting in the CSV |
| Stand-in setting | not_used_standin | Stand-in tests do not use paper retrieval |

## How this library will mislead a naive retriever

BM25 searches for matching words. It can rank a page highly because it shares words with a question, even when that page does not contain the best answer.

For example, a paper title page may rank above a page that explains the concept. This shows why retrieved passages should be checked before generating an answer.

## 6. Retries

I did not complete a proper retry experiment with the real Groq service.

My CSV contains a retry-test record, but the retry count is zero.

A future version should use exponential backoff. This means waiting longer before each new attempt when a rate limit occurs.

This can help reduce repeated failures.

## 7. What the person sees

The user enters a question about a research paper.

The system searches the research papers and finds relevant pages.

The Groq AI model uses those passages to generate an answer.

The answer includes the paper name and page number.

If the answer is not available in the papers, the system should say that it cannot find enough information.

## 8. What I'm unsure about, what I left out, what I learned

My experiment has some limitations:

- Only a few real Groq requests were successful.
- Nine quality questions were rate-limited.
- The stand-in is not exactly like the real Groq service.
- The stand-in token counts are approximate.
- My answer verifier cannot guarantee that every answer is factually correct.
- I did not measure the real service's maximum concurrent requests.
- I did not complete a proper retry experiment.

I learned how retrieval, response time, rate limits and errors affect an AI question-answering system.

## Your feedback on Vaani

I tried to visit vaaani.dev to explore the website.

However, the website did not open and showed a DNS_PROBE_FINISHED_NXDOMAIN error.

Because I could not access the website, I was unable to test its features or provide detailed feedback.

## How I worked with the assistant

I used ChatGPT for step-by-step guidance throughout this project.

It helped me understand Python errors, build the research-paper question-answering system, test the Groq API, analyze CSV results and prepare the report.

I followed the instructions and completed the project tasks myself.
