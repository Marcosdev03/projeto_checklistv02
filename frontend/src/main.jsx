import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

import './styles.css'

function mountApp() {
    const container = document.getElementById('root')
    if (!container) return false
    const root = createRoot(container)
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    )
    return true
}

// Se o elemento ainda não estiver presente (por algum motivo), aguarda DOMContentLoaded
if (!mountApp()) {
    document.addEventListener('DOMContentLoaded', () => {
        mountApp()
    })
}
