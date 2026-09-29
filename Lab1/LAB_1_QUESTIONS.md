*** Question 1 ***

List all parameters required to instantiate the OpenAI client.

*** Answer ***

api_key & base_url
client = OpenAI(
2
api_key=os.environ.get("AI_GW_API_KEY"),
3
base_url=os.environ.get("AI_GW_BASE_URL")
4
)

*** Question 2 ***

Paste the entire API response from OpenAI after running the basic azure completions code. Token count should be included.

*** Answer ***
OpenAI client initialized succesfully.
{
  "id": "chatcmpl-EIWbJu33ObhYLCE14j1RmKnhXGRz4",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "To compare productivity across Manila, Chennai, and Gurugram fairly and usefully, focus on quality-adjusted output per effective hour, normalized for case mix and context. Here’s a structured approach you can implement:\n\n1) Standardize what “productivity” means\n- Define a common unit of output: Use a standardized work taxonomy (work types, subtypes) across all sites.\n- Assign complexity weights: Base these on standard handling time or effort (e.g., a case with a 60-minute standard handling time is 3x a 20-minute case). This converts raw units into Weighted Completed Units (WCU).\n- Include quality and timeliness: Apply first-pass yield (FPY) and SLA adherence to avoid rewarding speed at the expense of quality. Quality-adjusted WCU = WCU × FPY × SLA compliance.\n\n2) Measure effective capacity rather than paid hours\n- Effective hours = Paid hours − shrinkage (planned/unplanned non-productive time like leave, breaks, meetings, training, system downtime).\n- Track utilization and occupancy separately:\n  - Utilization: time available for work divided by scheduled time.\n  - Occupancy: time actively working on cases divided by available time.\n- Use effective hours as the denominator; this removes differences caused by varying meeting loads, training ramps, or absenteeism.\n\n3) Core comparative metrics to calculate per site (and per workstream)\n- Quality-adjusted productivity: Quality-adjusted WCU per 100 effective hours.\n- SLA adherence: % of work completed within target time.\n- Rework rate: % of items needing rework or second touch; also rework hours as a % of total.\n- Cycle time: median and 80th percentile end-to-end cycle time, not just handle time.\n- AHT vs Standard: Actual Handling Time relative to Standard Handling Time (AHT/SHT ratio).\n- Capacity buffer: average cushion between capacity and demand (how often the site is in backlog risk).\n- Cost per quality-adjusted unit: Labor cost divided by quality-adjusted WCU.\n\n4) Normalize to get apples-to-apples\n- Case mix: Report by work type; apply complexity weights so sites with harder case mixes aren’t penalized.\n- Tenure and ramp: Segment performance by tenure buckets (e.g., 0–3 months, 4–12 months, 12+). New-hire ramps can distort site averages.\n- Shift and time-zone effects: Compare day vs night shifts separately; include local holiday calendars and overtime policies.\n- Tooling and automation: Note version differences, local network latency, and % of work aided by automation. Adjust expectations or at least call out these variances in interpretation.\n\n5) Diagnostic breakdowns\n- By workstream and queue: Compare like-for-like streams first; only then roll up to site-level views.\n- By supervisor/coach: Coaching intensity and span of control often explain performance variance.\n- By defect type: Identify where quality losses occur (documentation vs data entry vs judgment).\n- By demand pattern: Seasonal spikes or volatile volumes may impact cycle time and occupancy.\n\n6) Build a site productivity index\n- Compute a normalized index for each site: PI = (Quality-adjusted WCU per 100 effective hours) / baseline standard rate.\n- Use multivariate controls if you can: Run a simple regression controlling for case mix, tenure, shift, and automation level to estimate residual site effect. This helps isolate genuine site productivity differences.\n\n7) Compare trend and stability, not just averages\n- Use weekly trend lines and control charts to assess stability.\n- Track variance: A site with slightly lower average productivity but high stability may be more reliable for SLA-critical work.\n\n8) Risks to avoid in comparison\n- Comparing raw volumes or AHT alone: Ignores complexity and quality.\n- Not accounting for rework: Inflates apparent productivity.\n- Ignoring shrinkage differences: Penalizes sites with higher mandated training or meeting loads.\n- Metric gaming: Overemphasis on speed can drive quality issues; include FPY and QA audits.\n- Data definition drift: Inconsistent “completed” criteria across sites will corrupt comparisons.\n\n9) Bottlenecks to look for\n- High rework or low FPY in specific work types: Indicates training or SOP gaps.\n- Elevated shrinkage or downtime: System stability, tool latency, or excess non-operational meetings.\n- Low cross-skilling: Limits load balancing across queues and creates idle time in one stream while another is overloaded.\n- Ramp-heavy workforce: Persistent pipeline of new hires suppressing averages.\n- Capacity-time misalignment: Backlogs building during certain hours due to weak coverage alignment with demand.\n\n10) Opportunities to act on\n- Best-practice transfer: Identify top-performing microprocesses or SOPs in one site and replicate across others.\n- Case routing by strengths: Assign complex or high-judgment work to teams with higher FPY; route simpler volumes to scale centers.\n- Cross-skill and flexible staffing: Increase multi-skill coverage to reduce idle time and improve intraday load balancing.\n- Automation and tooling: Share macros, templates, and assist tools; prioritize fixing tool latency where it drags occupancy.\n- Coaching leverage: Optimize supervisor spans, implement targeted quality coaching based on defect hotspots.\n- Scheduling optimization: Align shifts with demand peaks; reduce shrinkage with smarter meeting/training windows.\n- Tenure shaping: Retention programs to improve average tenure in sites with heavy ramp churn.\n\n11) Recommended dashboard layout\n- Capacity: FTE, paid hours, effective hours, utilization, occupancy, shrinkage.\n- Output: WCU, Quality-adjusted WCU, rework rate, FPY, SLA adherence.\n- Efficiency: AHT/SHT ratio, cycle time percentiles, cost per quality-adjusted unit.\n- Stability: Weekly trends, control limits, backlog levels and aging.\n- Context: Case mix distribution, tenure buckets, shift mix, automation usage, tool health metrics.\n\nIf you share recent data for these sites (volumes by work type, AHT/SHT, FPY, shrinkage, effective hours, costs), I can run the normalization and produce a side-by-side comparison, identify the main drivers behind differences, and recommend targeted actions per site.",
        "refusal": null,
        "role": "assistant",
        "annotations": [],
        "audio": null,
        "function_call": null,
        "tool_calls": null,
        "provider_specific_fields": {
          "refusal": null
        }
      },
      "provider_specific_fields": {
        "content_filter_results": {
          "hate": {
            "filtered": false,
            "severity": "safe"
          },
          "protected_material_code": {
            "detected": false,
            "filtered": false
          },
          "protected_material_text": {
            "detected": false,
            "filtered": false
          },
          "self_harm": {
            "filtered": false,
            "severity": "safe"
          },
          "sexual": {
            "filtered": false,
            "severity": "safe"
          },
          "violence": {
            "filtered": false,
            "severity": "safe"
          }
        }
      }
    }
  ],
  "created": 1788083929,
  "model": "gpt-5",
  "object": "chat.completion",
  "metadata": null,
  "moderation": null,
  "service_tier": "default",
  "system_fingerprint": null,
  "usage": {
    "completion_tokens": 3199,
    "prompt_tokens": 53,
    "total_tokens": 3252,
    "completion_tokens_details": {
      "accepted_prediction_tokens": 0,
      "audio_tokens": 0,
      "reasoning_tokens": 1920,
      "rejected_prediction_tokens": 0,
      "text_tokens": null
    },
    "compute_units": null,
    "prompt_tokens_details": {
      "audio_tokens": 0,
      "cache_write_tokens": null,
      "cached_tokens": 0,
      "image_tokens": null,
      "text_tokens": null
    },
    "latency_checkpoint": {
      "engine_tbt_ms": 8,
      "engine_ttft_ms": 40,
      "engine_ttlt_ms": 24536,
      "pre_inference_ms": 154,
      "service_tbt_ms": 8,
      "service_ttft_ms": 551,
      "service_ttlt_ms": 25068,
      "total_duration_ms": 24920,
      "user_visible_ttft_ms": 396
    }
  },
  "prompt_filter_results": [
    {
      "prompt_index": 0,
      "content_filter_results": {
        "hate": {
          "filtered": false,
          "severity": "safe"
        },
        "jailbreak": {
          "detected": false,
          "filtered": false
        },
        "self_harm": {
          "filtered": false,
          "severity": "safe"
        },
        "sexual": {
          "filtered": false,
          "severity": "safe"
        },
        "violence": {
          "filtered": false,
          "severity": "safe"
        }
      }
    }
  ],
  "rate_limit": {
    "source": "headers",
    "requests": {
      "remaining": 29999,
      "limit": 30000
    },
    "tokens": {
      "remaining": 2999947,
      "limit": 3000000
    }
  }
}


*** Question 3 ***

How many tokens were in the prompt? How many tokens are in the response? How does this affect the cost of running the application?

*** Answer ***
"completion_tokens": 3199,
"prompt_tokens": 53,
"total_tokens": 3252,
"reasoning_tokens": 1920,

Token usage affects application cost because AI services typically charge based on the number of tokens processed. Larger prompts and longer responses consume more tokens and may increase costs. In this example, most token usage came from generating the response rather than processing the prompt. The 320 reasoning tokens indicate additional model processing used to create the final answer.

*** Question 4 ***

Adjust the print(response) statement so that it only prints the message content, and not the entire API response. Where is the generated text nested in the response?

*** Answer ***

print(response.choices[0].message.content)

Business users typically only need the generated answer, while developers may use the remaining response information for logging, monitoring, troubleshooting, and tracking token usage. Therefore, printing only the message content provides a cleaner user experience for only what is necessary.

#==output==
Start with an apples-to-apples framework so you don’t reward speed at the expense of quality or penalize teams taking on harder work. Here’s a practical way to compare Manila, Chennai, and Gurugram operations teams fairly and actionably.

1) Normalize work before comparing
- Create a common taxonomy of work types. Group tasks/cases into clear categories (e.g., low/medium/high complexity or by process type). Align definitions across sites.
- Assign complexity weights. Use historical cycle time or average handle time to derive weights (e.g., a task that typically takes 3× longer than baseline gets a weight of 3). Validate with SMEs and QA data; revisit quarterly.
- Standardize quality scoring. Use the same QA rubric, defect definitions, first-pass yield calculation, and rework rules at all sites. Align calibration across QA teams.

2) Define “productive time” consistently
- Productive hours = scheduled hours minus planned shrinkage (PTO, training, meetings) minus unplanned shrinkage (sick, outages), multiplied by schedule adherence.
- Track and report shrinkage categories uniformly so differences in attendance or meeting load don’t contaminate comparisons.

3) Core metrics to calculate per site
- Weighted throughput per productive hour: sum of complexity points completed divided by productive hours. This is your primary productivity metric.
- Quality adjustment: multiply weighted throughput by a quality factor such as first-pass yield (e.g., 0.95 if 95% pass QA without rework). Alternatively subtract rework points so you only count net completed work.
- Cycle time and backlog health: median cycle time by work type; backlog change rate; SLA attainment on timeliness.
- Utilization and adherence: occupancy/active work ratio; schedule adherence; percent of time in work vs aux/breaks.
- Cost per weighted unit: total labor cost (wages + benefits + overhead) divided by weighted units completed. This shows financial efficiency.
- Stability/resilience: overtime share, unplanned shrinkage rate, agent tenure mix, attrition, and supervisor-to-agent ratio.

4) Build composite indices
- Operational Productivity Index: weighted units per productive hour multiplied by quality factor. Use this for “how effectively do they turn time into correct output.”
- Financial Efficiency Index: cost per weighted unit. Use this to guide volume placement.
- Reliability Index: SLA attainment, backlog drift, and adherence combined to reflect delivery consistency.

5) Segment the comparison to avoid false conclusions
- By work type and complexity tier: compare Manila vs Chennai vs Gurugram within the same task categories.
- By shift and time zone alignment: Manila (UTC+8) vs Chennai/Gurugram (UTC+5:30) may face different arrival patterns; compare similar customer-facing windows or control for arrival variability.
- By tenure bands: ramping agents vs tenured. Normalize for mix; use cohort analysis.
- By tooling/automation level: if one site uses macros or bots others don’t, measure “human-only” throughput and separately track “automation-assisted” output.

6) How to run the analysis step-by-step
- Week 1: Align taxonomy, QA rubric, shrinkage definitions, and data fields across sites. Pull 8–12 weeks of history.
- Week 2: Derive complexity weights from median handle/cycle time. Validate with SMEs and QA. Freeze weights for the comparison period.
- Week 3: Compute per-site metrics: productive hours, weighted throughput/hour, quality factor, cost per weighted unit, SLA and backlog metrics. Build per-agent distributions to spot outliers.
- Week 4: Compare within matched segments (same work types, shifts, tenure bands). Use control charts or confidence intervals to separate signal from noise. Identify drivers via regression: which factors explain site differences.

7) Interpreting outcomes and making decisions
- If a site shows higher weighted throughput but lower quality, prioritize coaching, QA calibration, or rework prevention rather than moving more volume there immediately.
- If a site has best cost per weighted unit with acceptable quality, shift routine volume there. Keep complex or high-risk work where first-pass yield is strongest.
- If cycle times differ mainly due to arrival spikes or tooling, address scheduling or technology before concluding team performance differences.

8) Risks and bottlenecks to watch
- Apples-to-oranges QA or shrinkage tracking: misaligned definitions will skew results.
- Work mix bias: if one site handles more high-complexity tasks, raw throughput will look lower without weights.
- Data gaps: inconsistent timestamps or missing rework tagging hides true effort.
- Ramp and attrition: high proportions of new hires depress productivity; segment by tenure.
- Tooling and infrastructure: system lag or limited automation can bottleneck a site.
- Gaming risk: overemphasis on speed can increase hidden rework; require quality-adjusted metrics.

9) Opportunities you can unlock
- Skills-based routing: send complex cases to the site with highest first-pass yield; routine volume to the lowest cost per weighted unit.
- Best-practice sharing: replicate top performers’ workflows, templates, and macros across sites.
- Schedule optimization: align staffing to arrival patterns by site; reduce unplanned shrinkage and overtime.
- Automation parity: roll out effective tools across sites to neutralize tool-based advantages.
- Targeted training: focus on error-prone steps uncovered by QA to lift quality without sacrificing throughput.

10) Practical formulas (described simply)
- Productive hours = scheduled hours × adherence − planned shrinkage − unplanned shrinkage.
- Weighted throughput/hour = sum of task complexity points completed ÷ productive hours.
- Quality-adjusted productivity = weighted throughput/hour × first-pass yield.
- Cost per weighted unit = total labor cost ÷ sum of task complexity points completed.

11) Visualize and review
- Site-level dashboards with trend lines for weighted throughput/hour, quality, and cost per weighted unit.
- Distribution plots per agent to identify coaching needs or process blockers.
- Backlog and SLA heatmaps by work type and site.

With this approach, your comparisons will reflect true performance differences rather than artifacts of work mix, quality standards, or time accounting. It also gives you a clear path to act: where to send which work, what to fix, and how to staff optimally across Manila, Chennai, and Gurugram.

*** Question 5 ***

Explain the use of setting the system role when calling chat completions. What happens when we restrict the system role to a specific topic or response type? How can we use this to our advantage in our applications?

*** Answer ***

The system role is similar to assigning a job title and responsibilities to an employee before giving them a task. The AI uses those instructions to decide how to think about the request and how to present the answer.

When I assigned the AI the role of a Workforce Capacity Planning Expert, it responded like a consultant by discussing staffing utilization, productivity measurement, operational risks, bottlenecks, and recommendations for comparing teams across Manila, Chennai, and Gurugram.

This demonstrates that the same AI can be used for many business functions simply by changing the role it is given. Organizations can create specialized assistants for managers, analysts, developers, customer service representatives, or executives without changing the underlying AI model.

The system role improves consistency, keeps responses focused on the desired subject area, and helps ensure the information is tailored for the intended audience and business need.

**************