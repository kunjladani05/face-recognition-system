# Django Face Recognition System

This is a Django-based face recognition system that allows users to upload images and detect faces. The system checks the uploaded images against stored user profiles, matches detected faces with known profiles, and provides visual feedback with rectangles drawn around matched and unmatched faces.

## Features

- **Image Upload**: Users can upload images for face recognition.
- **Face Matching**: The system compares uploaded faces with stored user profiles.
- **Live Recognition**: Real-time recognition via webcam capture.
- **Face Location Highlighting**: Draws green rectangles around matched faces and red rectangles around unmatched faces.
- **Activity Logging**: Logs successful face recognition events for tracking.

## Requirements

- Python 3.x
- Django 3.x or higher
- OpenCV (`opencv-python`)
- Face Recognition library
- Pillow (for image handling)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/django-face-recognition.git
    ```

2. Navigate to the project directory:

    ```bash
    cd FaceRecognitionSystem
    ```

3. Create a virtual environment:

    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    - **Windows**: `venv\Scripts\activate`
    - **Linux/macOS**: `source venv/bin/activate`

5. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Set up your database:

    ```bash
    python manage.py migrate
    ```

7. Create a superuser (optional, for admin access):

    ```bash
    python manage.py createsuperuser
    ```

8. Start the development server:

    ```bash
    python manage.py runserver
    ```

9. Visit `http://127.0.0.1:8000/` to access the application.

## Configuration

### Face Recognition Setup

- **UserProfile Model**: Stores user information and their profile images.
    - `image`: The profile image for each user.
    - `name`: The user's full name.
    - `phone_number`: User's contact number.
    - `email`: Unique email for each user.
    - `address`: User's physical address.
    - `date_of_birth`: User's date of birth.

- **ActivityLog Model**: Tracks user actions, such as successful face recognition.

### Image Processing

- **Face Recognition** is handled using the `face_recognition` library, which provides easy-to-use methods for detecting and encoding faces.
- **OpenCV** is used for drawing rectangles around faces in images:
    - **Green Rectangles**: Drawn around faces that match a known user profile.
    - **Red Rectangles**: Drawn around faces that do not match any stored profiles.

### File Storage

- Images are stored in `MEDIA_ROOT` (set in `settings.py`), and uploaded images are saved with unique filenames.
- **Additional Profile Images**: Users can upload multiple images, which are stored in a path based on their email address.

## Templates

- **upload_photo.html**: The template for uploading a photo and viewing face recognition results.
- **live_recognition.html**: Template for live webcam capture and face recognition.
- **dashboard**: Admin interface for managing user profiles, uploading images, and viewing activity logs.

## How to Use

### Upload Image for Face Recognition

1. Navigate to the face recognition page.
2. Upload an image file.
3. The system will process the image and draw rectangles around detected faces:
    - Green rectangles for matched faces.
    - Red rectangles for unmatched faces.
4. If a match is found, the system will display the user profile associated with the detected face.

### Live Recognition

1. Capture an image using your webcam.
2. The system will perform live face recognition and display matched profiles or an error message.

## Activity Logs

Each successful face recognition attempt is logged in the `ActivityLog` model with the following details:
- **User**: The user who initiated the recognition.
- **Action**: Description of the action (e.g., "Recognition success for John Doe").
- **Timestamp**: The date and time of the action.

## Troubleshooting

- Ensure that all required dependencies are installed.
- Check that the `MEDIA_ROOT` directory is correctly set up and writable.
- Make sure that the uploaded images are of good quality for face recognition (clear, well-lit, and centered).


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Face Recognition](https://github.com/ageitgey/face-recognition) for the face recognition library.
- [OpenCV](https://opencv.org/) for image processing and drawing rectangles.
- [Django](https://www.djangoproject.com/) for the web framework.

