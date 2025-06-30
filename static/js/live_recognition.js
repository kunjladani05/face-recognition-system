// Declare stream globally
let stream;

// Get video element and start webcam
const video = document.getElementById('video');
const videoWrapper = document.querySelector('.video-wrapper');
const cameraButton = document.getElementById('camera-button'); // The camera control button

// Function to start the webcam
function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(mediaStream => {
            stream = mediaStream; // Store the stream globally
            video.srcObject = stream;
            cameraButton.textContent = "Stop Camera"; // Change button text to 'Stop Camera'
        })
        .catch(err => {
            console.error("Error accessing webcam:", err);
            alert("Error accessing webcam. Please make sure you have granted camera permissions.");
        });
}

// Function to stop the webcam
function stopCamera() {
    if (stream) {
        let tracks = stream.getTracks();
        tracks.forEach(track => track.stop()); // Stop each track in the stream
    }
    video.srcObject = null; // Stop the video feed
    cameraButton.textContent = "Start Camera"; // Change button text back to 'Start Camera'
}

// Toggle the camera state (start or stop)
cameraButton.addEventListener('click', function () {
    if (cameraButton.textContent === "Start Camera") {
        startCamera(); // Start the camera if it's currently stopped
    } else {
        stopCamera(); // Stop the camera if it's currently running
    }
});

// Auto-start the camera on page load and set button to "Stop Camera"
window.addEventListener('DOMContentLoaded', function () {
    startCamera();  // Start the camera when the page loads
    cameraButton.textContent = "Stop Camera";  // Change the button text to "Stop Camera"
});

// Function to capture photo
function capturePhoto() {
    // Add scanning animation
    videoWrapper.classList.add('scanning');

    // Create canvas to capture frame
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;

    // Draw current video frame to canvas
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0);

    // Convert canvas to base64 image
    const imageData = canvas.toDataURL('image/jpeg');
    document.getElementById('captured_image').value = imageData;

    // Remove scanning animation after 2 seconds
    setTimeout(() => {
        videoWrapper.classList.remove('scanning');
    }, 2000);
}

// Auto-scroll to result or error section if present
window.addEventListener("DOMContentLoaded", function () {
    const profileSection = document.getElementById("profile-section");
    const errorMessage = document.getElementById("error-message");

    if (profileSection) {
        profileSection.scrollIntoView({ behavior: "smooth" });
    } else if (errorMessage) {
        errorMessage.scrollIntoView({ behavior: "smooth" });
    }
});
