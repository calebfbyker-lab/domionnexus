import OpenAI from 'openai'

// Subject ID binding (CFBK)
const SUBJECT_ID_SHA256 = '2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a'
const WORKFLOW_REF = 'wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e'
const WORKFLOW_VERSION = 5

export const handler = async (event) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  }

  // Handle OPTIONS request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    }
  }

  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    }
  }

  try {
    const { input_as_text } = JSON.parse(event.body || '{}')

    if (!input_as_text) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'input_as_text is required' })
      }
    }

    // Environment variables
    const apiKey = process.env.OPENAI_API_KEY
    const model = process.env.OPENAI_MODEL || 'gpt-4o-mini'
    const humanInLoop = process.env.HUMAN_IN_LOOP === 'true'
    const maxRuns = parseInt(process.env.AGENT_MAX_RUNS || '10', 10)

    if (!apiKey) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: 'OPENAI_API_KEY not configured' })
      }
    }

    // Initialize OpenAI client
    const openai = new OpenAI({ apiKey })

    // Provenance metadata
    const provenance = {
      subject_id_sha256: SUBJECT_ID_SHA256,
      workflow_ref: WORKFLOW_REF,
      workflow_version: WORKFLOW_VERSION,
      timestamp_utc: new Date().toISOString(),
      human_in_loop: humanInLoop,
      max_runs: maxRuns
    }

    // Extract workflow reference from input
    const workflowMatch = input_as_text.match(/^(wf_[a-f0-9]+)\s+version=(\d+):/)
    if (workflowMatch) {
      const [, inputWorkflowRef, inputVersion] = workflowMatch
      provenance.input_workflow_ref = inputWorkflowRef
      provenance.input_workflow_version = parseInt(inputVersion, 10)
      
      // Validate workflow reference matches
      if (inputWorkflowRef !== WORKFLOW_REF || parseInt(inputVersion, 10) !== WORKFLOW_VERSION) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({
            error: 'Workflow reference mismatch',
            expected: `${WORKFLOW_REF} version=${WORKFLOW_VERSION}`,
            provided: `${inputWorkflowRef} version=${inputVersion}`
          })
        }
      }
    }

    // Run the agent with provenance tracking
    const runs = []
    let currentInput = input_as_text
    
    for (let i = 0; i < maxRuns; i++) {
      const run = {
        run_number: i + 1,
        input: currentInput,
        timestamp_utc: new Date().toISOString()
      }

      // Call OpenAI API
      const response = await openai.chat.completions.create({
        model,
        messages: [
          {
            role: 'system',
            content: `You are a DomionNexus orchestration agent bound to subject_id_sha256: ${SUBJECT_ID_SHA256}. You help with knowledge integration, indexing, and safe orchestration tasks. Provide clear, structured responses.`
          },
          {
            role: 'user',
            content: currentInput
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      })

      const completion = response.choices[0]?.message?.content || ''
      
      run.output = completion
      run.finish_reason = response.choices[0]?.finish_reason
      run.usage = response.usage

      runs.push(run)

      // Check if we should continue
      if (humanInLoop && i === 0) {
        // In human-in-the-loop mode, stop after first run
        break
      }

      // Check for completion signals
      if (completion.toLowerCase().includes('task complete') || 
          completion.toLowerCase().includes('integration plan complete')) {
        break
      }

      currentInput = completion
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        provenance,
        runs,
        total_runs: runs.length,
        final_output: runs[runs.length - 1]?.output
      })
    }

  } catch (error) {
    console.error('Agent error:', error)
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: error.message,
        provenance: {
          subject_id_sha256: SUBJECT_ID_SHA256,
          workflow_ref: WORKFLOW_REF,
          workflow_version: WORKFLOW_VERSION,
          timestamp_utc: new Date().toISOString()
        }
      })
    }
  }
}
