// Wait until the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

  // Get reference to the drag-and-drop/upload area
  const uploadArea = document.getElementById('upload-area');

  // File input element for selecting files
  const fileInput = document.getElementById('file-upload');

  // Area that initially shows upload instructions or icon
  const uploadContent = document.getElementById('upload-content');

  // Container where the image preview is shown
  const previewContainer = document.getElementById('preview-container');

  // The <img> tag where the uploaded image will be displayed
  const previewImage = document.getElementById('preview-image');

  // Element to display error messages
  const errorMessage = document.getElementById('error-message');

  // Analyze button (used to trigger image analysis)
  const analyzeButton = document.getElementById('analyze-button');

  // The form that will be submitted when analyzing
  const uploadForm = document.getElementById('upload-form');

  // Function to show an error message and hide the analyze button
  const showError = (msg) => {
    errorMessage.querySelector('p').textContent = msg; // Set error text
    errorMessage.style.display = 'block';              // Show error div
    analyzeButton.style.display = 'none';              // Hide the analyze button
  };

  // Function to hide the error message
  const hideError = () => {
    errorMessage.style.display = 'none';               // Hide error message block
  };

  // Function to handle the selected or dropped file
  const handleFile = (file) => {
    if (!file) return;  // If no file is provided, do nothing

    // Check if the file is an image
    if (!file.type.startsWith('image/')) {
      showError('Please upload a valid image file.');
      return;
    }

    // If it's a valid image file, hide error message (if any)
    hideError();

    const reader = new FileReader();  // Create a FileReader to read the file

    // When the file is read, set the preview image and update UI
    reader.onload = (e) => {
      previewImage.src = e.target.result;          // Set image src to loaded base64 data
      uploadContent.style.display = 'none';        // Hide the default upload instructions/content
      previewContainer.style.display = 'block';    // Show the image preview section
      analyzeButton.style.display = 'inline-block';// Show the Analyze button
    };

    reader.readAsDataURL(file); // Start reading the image file as base64 string
  };

  // When the file input changes (user selects a file), handle it
  fileInput.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);  // Call handleFile with the selected file
  });

  // When the upload area is clicked, simulate a click on the file input
  uploadArea.addEventListener('click', () => {
    fileInput.click();  // Open the file picker dialog
  });

  // Function to handle drag-and-drop events (visual effect)
  const handleDrag = (e) => {
    e.preventDefault();   // Prevent default browser behavior
    e.stopPropagation();  // Stop event from bubbling up

    // Add or remove visual class based on event type
    if (e.type === 'dragenter' || e.type === 'dragover') {
      uploadArea.classList.add('drag-active');  // Highlight drop area
    } else if (e.type === 'dragleave') {
      uploadArea.classList.remove('drag-active'); // Remove highlight
    }
  };

  // Handle file drop onto the upload area
  const handleDrop = (e) => {
    e.preventDefault();     // Prevent default drop behavior
    e.stopPropagation();    // Stop event from bubbling

    uploadArea.classList.remove('drag-active');  // Remove drop area highlight

    const file = e.dataTransfer.files?.[0];  // Get the first dropped file
    handleFile(file);                        // Handle the dropped file

    fileInput.files = e.dataTransfer.files;  // Attach dropped files to the file input (important for form submission)
  };

  // Add drag/drop event listeners to the upload area
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    uploadArea.addEventListener(event, handleDrag);  // Add listeners for drag interaction
  });

  // Add a drop listener separately (to handle actual file dropping)
  uploadArea.addEventListener('drop', handleDrop);

  // Handle Analyze button click
  analyzeButton.addEventListener('click', (e) => {
    // If no file is selected, show an error and prevent form submission
    if (!fileInput.files.length) {
      e.preventDefault();  // Prevent form submission
      showError("Please upload a photo before analyzing.");
    }
  });

});
