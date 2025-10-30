// Netlify orchestrator function for managing agent tasks
const SUBJECT_ID_SHA256 = '2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a'

export const handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  }

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' }
  }

  try {
    const { action, task_id, data } = event.httpMethod === 'POST' 
      ? JSON.parse(event.body || '{}') 
      : { action: 'status' }

    const response = {
      subject_id_sha256: SUBJECT_ID_SHA256,
      timestamp_utc: new Date().toISOString(),
      action: action || 'status'
    }

    switch (action) {
      case 'status':
        response.status = 'operational'
        response.version = '1.0.0'
        response.capabilities = [
          'run-agent',
          'task-management',
          'provenance-tracking'
        ]
        break

      case 'submit_task':
        if (!data?.input_as_text) {
          return {
            statusCode: 400,
            headers,
            body: JSON.stringify({ error: 'input_as_text required for submit_task' })
          }
        }
        
        response.task_id = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        response.status = 'submitted'
        response.message = 'Task submitted for processing'
        break

      case 'get_task':
        if (!task_id) {
          return {
            statusCode: 400,
            headers,
            body: JSON.stringify({ error: 'task_id required for get_task' })
          }
        }
        
        response.task_id = task_id
        response.status = 'not_found'
        response.message = 'Task storage not yet implemented'
        break

      default:
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ error: `Unknown action: ${action}` })
        }
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(response)
    }

  } catch (error) {
    console.error('Orchestrator error:', error)
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: error.message,
        subject_id_sha256: SUBJECT_ID_SHA256
      })
    }
  }
}
