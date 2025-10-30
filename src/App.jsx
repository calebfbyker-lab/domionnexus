import React, { useState } from 'react'
import SigilEngine from './components/SigilEngine'
import './App.css'

function App() {
  const [agentInput, setAgentInput] = useState('')
  const [agentResponse, setAgentResponse] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleRunAgent = async () => {
    if (!agentInput.trim()) return
    
    setIsLoading(true)
    setAgentResponse(null)

    try {
      const response = await fetch('/.netlify/functions/run-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input_as_text: agentInput }),
      })

      const data = await response.json()
      setAgentResponse(data)
    } catch (error) {
      setAgentResponse({ error: error.message })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="canvas-container">
        <SigilEngine />
      </div>
      
      <div className="control-panel">
        <div className="header">
          <h1>🌌 DomionNexus</h1>
          <p className="subtitle">Sigil Engine · CFBK Edition</p>
          <p className="subject-id">
            Subject ID: <code>2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a</code>
          </p>
        </div>

        <div className="agent-interface">
          <h2>Agent Runner</h2>
          <textarea
            value={agentInput}
            onChange={(e) => setAgentInput(e.target.value)}
            placeholder="Enter workflow reference and task (e.g., wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e version=5: propose an integration plan...)"
            rows={4}
          />
          
          <button onClick={handleRunAgent} disabled={isLoading || !agentInput.trim()}>
            {isLoading ? 'Running Agent...' : 'Run Agent'}
          </button>

          {agentResponse && (
            <div className="response">
              <h3>Response:</h3>
              <pre>{JSON.stringify(agentResponse, null, 2)}</pre>
            </div>
          )}
        </div>

        <div className="info">
          <h3>Deployment Info</h3>
          <ul>
            <li>Workflow: wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e version=5</li>
            <li>Build: Vite + React Three Fiber</li>
            <li>Integrity: See dist/integrity.json after build</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
