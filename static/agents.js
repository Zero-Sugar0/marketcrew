document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('project-form');
    const startButton = document.getElementById('start-button');
    const activeAgentSpan = document.getElementById('active-agent');
    const researcherOutput = document.querySelector('#researcher-output .output-content');
    const competitorAnalystOutput = document.querySelector('#competitor-analyst-output .output-content');
    const contentWriterOutput = document.querySelector('#content-writer-output .output-content');

    const socket = io();

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const companyName = document.getElementById('company-name').value;
        const industry = document.getElementById('industry').value;
        const mainProducts = document.getElementById('main-products').value;

        // Clear previous outputs
        researcherOutput.textContent = '';
        competitorAnalystOutput.textContent = '';
        contentWriterOutput.textContent = '';

        // Update button state and text
        startButton.disabled = true;
        startButton.textContent = 'Agents Running...';

        // Reset active agent display
        activeAgentSpan.textContent = 'Starting...';

        // Send data to backend via Socket.io
        socket.emit('start_agents', { companyName, industry, mainProducts });
    });

    socket.on('researcher_output', (data) => {
        appendOutput(researcherOutput, data);
        activeAgentSpan.textContent = 'Market Research Specialist';
    });

    socket.on('competitor_analyst_output', (data) => {
        appendOutput(competitorAnalystOutput, data);
        activeAgentSpan.textContent = 'Competitive Intelligence Analyst';
    });

    socket.on('content_writer_output', (data) => {
        appendOutput(contentWriterOutput, data);
        activeAgentSpan.textContent = 'Content Strategist and Copywriter';
    });

    socket.on('agents_complete', () => {
        startButton.disabled = false;
        startButton.textContent = 'Start Agents';
        activeAgentSpan.textContent = 'Complete';
    });

    function appendOutput(element, data) {
        element.textContent += data + '\n';
        element.scrollTop = element.scrollHeight;
    }
});