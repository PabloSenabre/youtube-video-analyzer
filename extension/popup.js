document.addEventListener('DOMContentLoaded', function() {
  const getCurrentUrlButton = document.getElementById('getCurrentUrlButton');
  const youtubeUrlInput = document.getElementById('youtube-url');
  const customPromptInput = document.getElementById('custom-prompt');
  const analyzeButton = document.getElementById('analyze-button');
  const resultDiv = document.getElementById('resultContent');
  const darkModeToggle = document.getElementById('darkModeToggle');
  const charCount = document.getElementById('charCount');
  const copyResultsButton = document.getElementById('copyResults');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');

  // Tab functionality
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabName = button.getAttribute('data-tab');
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabContents.forEach(content => content.classList.remove('active'));
      button.classList.add('active');
      document.getElementById(`${tabName}Tab`).classList.add('active');
    });
  });

  // Dark mode toggle
  darkModeToggle.addEventListener('change', () => {
    document.body.classList.toggle('dark-mode');
  });

  // Character count for custom prompt
  customPromptInput.addEventListener('input', () => {
    const count = customPromptInput.value.length;
    charCount.textContent = `${count} / 500`;
    if (count > 500) {
      charCount.style.color = '#ff0000';
    } else {
      charCount.style.color = '';
    }
  });

  getCurrentUrlButton.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs[0].url.includes("youtube.com/watch")) {
        resultDiv.textContent = "Error: No es una página de video de YouTube válida";
        return;
      }
      
      youtubeUrlInput.value = tabs[0].url;
      resultDiv.textContent = "URL del video obtenida correctamente.";
    });
  });

  analyzeButton.addEventListener('click', function() {
    const youtubeUrl = youtubeUrlInput.value;
    const customPrompt = customPromptInput.value;

    if (!youtubeUrl) {
      resultDiv.textContent = "Error: Por favor, introduce una URL de YouTube";
      return;
    }

    loadingOverlay.classList.remove('hidden');
    resultDiv.textContent = "Analizando...";
    analyzeButton.disabled = true;

    fetch('https://f2fb2128-3e97-420d-be27-704821ab1083-00-23yumzih2ro83.kirk.replit.dev/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        youtube_url: youtubeUrl,
        custom_prompt: customPrompt
      }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      resultDiv.innerText = data.analysis;
      copyResultsButton.style.display = 'block';
      document.querySelector('[data-tab="results"]').click();
    })
    .catch((error) => {
      console.error('Error:', error);
      resultDiv.innerText = `Error al analizar el video: ${error.message}`;
    })
    .finally(() => {
      loadingOverlay.classList.add('hidden');
      analyzeButton.disabled = false;
    });
  });

  copyResultsButton.addEventListener('click', () => {
    navigator.clipboard.writeText(resultDiv.innerText).then(() => {
      const originalText = copyResultsButton.textContent;
      copyResultsButton.textContent = "¡Copiado!";
      setTimeout(() => {
        copyResultsButton.textContent = originalText;
      }, 2000);
    });
  });
});