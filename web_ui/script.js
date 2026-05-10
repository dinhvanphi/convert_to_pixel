document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const uploadContent = document.getElementById('upload-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    
    const colorSlider = document.getElementById('colors');
    const colorVal = document.getElementById('color-val');
    const gridRadios = document.querySelectorAll('input[name="grid"]');
    
    const inputs = {
        id: document.getElementById('artwork-id'),
        title: document.getElementById('title'),
        category: document.getElementById('category'),
        preview: document.getElementById('preview'),
        output: document.getElementById('output'),
        append: document.getElementById('append')
    };
    
    const runBtn = document.getElementById('run-btn');
    
    // Results DOM Elements
    const executionResults = document.getElementById('execution-results');
    const generatedImage = document.getElementById('generated-image');
    const downloadJson = document.getElementById('download-json');
    const downloadImg = document.getElementById('download-img');
    const executionLogs = document.getElementById('execution-logs');

    let currentFile = null;

    // File Upload Handling
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering upload click
        currentFile = null;
        fileInput.value = '';
        previewContainer.style.display = 'none';
        uploadContent.style.display = 'block';
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadContent.style.display = 'none';
            previewContainer.style.display = 'block';
            
            // Auto-fill ID and Title based on filename if they are empty
            const fileNameWithoutExt = file.name.split('.').slice(0, -1).join('.');
            if (!inputs.id.value) inputs.id.value = fileNameWithoutExt.toLowerCase().replace(/\s+/g, '_');
            if (!inputs.title.value) inputs.title.value = fileNameWithoutExt;
        };
        
        reader.readAsDataURL(file);
    }

    // Color Slider Update
    colorSlider.addEventListener('input', (e) => {
        colorVal.textContent = e.target.value;
    });



    // Run Command Button Logic
    runBtn.addEventListener('click', async () => {
        if (!currentFile) {
            alert("Please upload an image first!");
            return;
        }

        const originalHtml = runBtn.innerHTML;
        runBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Running...';
        runBtn.disabled = true;
        executionResults.style.display = 'none';

        try {
            const formData = new FormData();
            formData.append('image', currentFile);
            
            const gridValue = document.querySelector('input[name="grid"]:checked').value;
            formData.append('grid', gridValue);
            formData.append('colors', colorSlider.value);
            
            if (inputs.id.value) formData.append('id', inputs.id.value);
            if (inputs.title.value) formData.append('title', inputs.title.value);
            formData.append('category', inputs.category.value);
            if (inputs.preview.value) formData.append('preview', inputs.preview.value);
            if (inputs.output.value) formData.append('output', inputs.output.value);
            if (inputs.append.checked) formData.append('append', 'true');

            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Server error');
            }

            // Show results
            executionResults.style.display = 'block';
            generatedImage.src = result.preview_url + "?t=" + new Date().getTime(); // Prevent caching
            
            // Setup download links
            downloadImg.href = result.preview_url;
            downloadJson.href = result.json_url;
            
            // Set dynamic download filename
            const filenameNoExt = currentFile.name.split('.').slice(0, -1).join('.');
            downloadImg.download = filenameNoExt + '_preview.png';
            downloadJson.download = inputs.output.value || 'artworks.json';

            // Show logs
            executionLogs.textContent = result.logs || "Success!";
            
        } catch (error) {
            alert("Error: " + error.message);
        } finally {
            runBtn.innerHTML = originalHtml;
            runBtn.disabled = false;
        }
    });
});
