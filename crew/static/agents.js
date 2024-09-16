document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('project-form');
    const researcherOutput = document.querySelector('#researcher-output .output-content');
    const competitorAnalystOutput = document.querySelector('#competitor-analyst-output .output-content');
    const contentWriterOutput = document.querySelector('#content-writer-output .output-content');

    // Initialize Socket.io
    const socket = io('http://your-render-backend-url');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const companyName = document.getElementById('company-name').value;
        const industry = document.getElementById('industry').value;
        const mainProducts = document.getElementById('main-products').value;

        // Clear previous outputs
        researcherOutput.textContent = '';
        competitorAnalystOutput.textContent = '';
        contentWriterOutput.textContent = '';

        // Send data to backend
        socket.emit('start_agents', { companyName, industry, mainProducts });
    });

    // Listen for agent outputs
    socket.on('researcher_output', (data) => {
        appendOutput(researcherOutput, data);
    });

    socket.on('competitor_analyst_output', (data) => {
        appendOutput(competitorAnalystOutput, data);
    });

    socket.on('content_writer_output', (data) => {
        appendOutput(contentWriterOutput, data);
    });

    function appendOutput(element, data) {
        element.textContent += data + '\n';
        element.scrollTop = element.scrollHeight;
    }
});