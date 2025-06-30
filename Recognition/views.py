from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
import numpy as np
from datetime import datetime
import face_recognition
import cv2
import uuid
import base64
import os
from django.conf import settings
from django.views import View
from .models import *
from .forms import *

# > > > > > > > Login And Signup Views Function Start < < < < < < <
# View to handle user signup
def SignupPage(request):
    """
       Handles the user signup process. This view function processes both GET and POST requests:
       - On GET request: Renders the signup page.
       - On POST request: Validates the form data, checks for existing usernames, ensures passwords match,
         creates a new user if all checks pass, and displays appropriate success or error messages.

       POST data is expected to contain:
       - 'username': The desired username for the new user.
       - 'email': The email address for the new user.
       - 'password1': The desired password for the new user.
       - 'password2': A confirmation of the password for the new user.

       If the username already exists in the database or if the passwords do not match, error messages will
       be displayed. Otherwise, a new user is created, and the user is redirected to the login page with a success message.

       Args:
       request: The HTTP request object containing the request data.

       Returns:
       A rendered template for the signup page or a redirect to the login page depending on the request method and form validation.
       """
    # Check if the request method is POST (i.e., form submitted)
    if request.method == 'POST':
        # Get the form values from the submitted data
        uname = request.POST.get('username')     # Get the username
        email = request.POST.get('email')        # Get the email
        pass1 = request.POST.get('password1')    # Get the password
        pass2 = request.POST.get('password2')    # Get the confirm password

        # Check if the username already exists in the database
        if User.objects.filter(username=uname).exists():
            # If username exists, show an error message and redirect to signup page
            messages.error(request, "Username already exists. Please choose a different one.")
            return redirect('signup')

        # Check if both entered passwords match
        if pass1 != pass2:
            # If passwords don't match, show an error and redirect to signup page
            messages.error(request, "Your password and confirm password do not match.")
            return redirect('signup')

        # If all checks pass, create a new user
        my_user = User.objects.create_user(username=uname, email=email, password=pass1)
        my_user.save()  # Save the user to the database

        # Show a success message and redirect to login page
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect('login')

    # If request method is GET, render the signup page
    return render(request, 'signup.html')

# View to handle user login
def LoginPage(request):
    """
       Handles the user login process. This view function processes both GET and POST requests:
       - On GET request: Renders the login page.
       - On POST request: Validates the form data, attempts to authenticate the user, and handles login.

       POST data is expected to contain:
       - 'username': The username of the user trying to log in.
       - 'pass': The password of the user trying to log in.

       If authentication is successful, the user is logged in, and the activity is recorded in the ActivityLog model.
       Based on the user type (Admin or Regular User), the user is redirected to either the dashboard (for Admin) or the home page (for Regular User).
       If authentication fails, an error message is displayed.

       Args:
       request: The HTTP request object containing the login form data.

       Returns:
       A rendered template for the login page or a redirect to the appropriate page (dashboard/home) depending on the authentication result.
       """
    # Check if the request method is POST (i.e., login form submitted)
    if request.method == 'POST':
        # Get the form values for username and password
        username = request.POST.get('username')  # Get the username from form
        pass1 = request.POST.get('pass')         # Get the password from form

        # Authenticate the user (checks username and password)
        user = authenticate(request, username=username, password=pass1)

        # If authentication is successful
        if user is not None:
            # Log the user in
            login(request, user)

            # Determine the type of user (Admin or Regular User)
            user_type = "Admin" if user.is_superuser else "User"

            # Log the login activity in the ActivityLog model
            ActivityLog.objects.create(
                user=user,
                action="Login",
                details=f"{user_type} logged in"
            )

            # Redirect based on user type
            if user.is_superuser:
                return redirect('dashboard')  # Superuser goes to the dashboard
            else:
                return redirect('home')  # Regular user goes to the home page
        else:
            # If authentication fails, show an error message
            return render(request, 'login.html', {'error_message': 'Invalid user details'})

    # If request method is GET, render the login page
    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

# > > > > > > > Login and Signup View Function End < < < < < < <

# > > > > > > > Home page View Function Start < < < < < < <
@login_required
def HomePage(request):
    return render(request, "home.html")

def imagePreview(request):
    return render(request, "imagePreview.html")

# View to handle photo upload and face recognition
def UploadPhoto(request):
    """
        Handles the uploading and facial recognition of an image uploaded by the user. This view function processes
        POST requests containing an image file, performs facial recognition on the uploaded image, and compares the
        detected faces with known profiles stored in the database.

        The process is as follows:
        - The image file is uploaded via the request.
        - The image is temporarily saved to the server.
        - Facial recognition is performed on the uploaded image, and the detected faces are compared to the known
          profiles stored in the database.
        - Green rectangles are drawn around faces that match known profiles, while red rectangles are drawn around
          faces that do not match any profile.
        - If a match is found, the matched profile is added to the list of matched profiles and the recognition event
          is logged.
        - The final image (with rectangles drawn) is saved and returned to the user with a link to the image and the
          matched profiles.

        POST data is expected to contain:
        - 'photo': The image file uploaded by the user.

        If faces are detected in the image, they are compared with the known profiles in the database. If a match is
        found, the corresponding profile name is displayed along with the modified image containing the matching faces
        outlined in green. If no match is found, the faces are outlined in red and labeled as "Unknown".

        If no faces are detected in the uploaded image, an error message is displayed.

        Args:
        request: The HTTP request object containing the uploaded image.

        Returns:
        A rendered template with the modified image containing rectangles around recognized faces and matching profile
        details, or an error message if no faces were detected or no matches were found in the database.
    """

    matched_profiles = []  # List to store all matched profiles

    # Check if the request is POST and a file named 'photo' is uploaded
    if request.method == 'POST' and request.FILES.get('photo'):
        uploaded_image = request.FILES['photo']  # Get the uploaded file

        # Save uploaded file temporarily
        temp_image_path = os.path.join(settings.MEDIA_ROOT,
                                       'temp_uploaded.jpg')  # Set a temporary path to save uploaded image
        with open(temp_image_path, 'wb') as f:  # Open the file in write-binary mode
            for chunk in uploaded_image.chunks():  # Write the uploaded file in chunks
                f.write(chunk)

        # Load uploaded image into an array (RGB format)
        uploaded_image_array = face_recognition.load_image_file(temp_image_path)
        uploaded_image_encodings = face_recognition.face_encodings(
            uploaded_image_array)  # Extract face encodings from the uploaded image
        face_locations = face_recognition.face_locations(
            uploaded_image_array)  # Find face locations in the uploaded image

        if uploaded_image_encodings and face_locations:  # If faces are detected
            known_encodings = []  # List to store known face encodings from database
            known_profiles = []  # List to store corresponding profiles

            # Load database profiles to compare
            for profile in UserProfile.objects.all():  # Loop through all user profiles
                profile_image_path = os.path.join(settings.MEDIA_ROOT,
                                                  profile.image.name)  # Build full path to profile image
                if os.path.exists(profile_image_path):  # Check if profile image file exists
                    profile_image = face_recognition.load_image_file(profile_image_path)  # Load profile image
                    profile_encodings = face_recognition.face_encodings(profile_image)  # Extract face encodings
                    if profile_encodings:
                        known_encodings.append(profile_encodings[0])  # Save first face encoding
                        known_profiles.append(profile)  # Save the profile object

            matched_profiles = []  # To store matched profiles
            uploaded_image_bgr = cv2.cvtColor(uploaded_image_array,
                                              cv2.COLOR_RGB2BGR)  # Convert image to BGR for OpenCV (as OpenCV uses BGR format)

            # Font settings for writing text on image
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2

            # Loop through each detected face in uploaded image
            for i, uploaded_face_encoding in enumerate(uploaded_image_encodings):
                matches = face_recognition.compare_faces(
                    known_encodings,
                    uploaded_face_encoding,
                    tolerance=0.6  # Compare uploaded face with known faces with 0.6 flexibility
                )
                face_distances = face_recognition.face_distance(
                    known_encodings,
                    uploaded_face_encoding
                )

                best_match_index = None
                if face_distances.size > 0:
                    best_match_index = face_distances.argmin()  # Find index of best (smallest distance) match

                (top, right, bottom, left) = face_locations[i]  # Get coordinates of detected face

                if best_match_index is not None and face_distances[best_match_index] < 0.6:
                    matched_profile = known_profiles[best_match_index]  # Get matched profile

                    # Draw green rectangle around matched face
                    cv2.rectangle(uploaded_image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)

                    # Prepare name text and background box
                    name_text = matched_profile.name
                    text_size, _ = cv2.getTextSize(name_text, font, font_scale, thickness)
                    text_width, text_height = text_size

                    # Draw green background rectangle above face
                    cv2.rectangle(uploaded_image_bgr, (left, top - text_height - 10), (left + text_width + 10, top),
                                  (0, 255, 0), cv2.FILLED)

                    # Put the name text over the rectangle
                    cv2.putText(uploaded_image_bgr, name_text, (left + 5, top - 5), font, font_scale, (0, 0, 0),
                                thickness)

                    # Add matched profile only once
                    if matched_profile not in matched_profiles:
                        matched_profiles.append(matched_profile)

                        # Log the successful recognition in ActivityLog
                        ActivityLog.objects.create(
                            user=request.user,
                            action=f"Recognition success for {matched_profile.name}"
                        )
                else:
                    # Draw red rectangle around unmatched face
                    cv2.rectangle(uploaded_image_bgr, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Prepare "Unknown" text and background
                    unknown_text = "Unknown"
                    text_size, _ = cv2.getTextSize(unknown_text, font, font_scale, thickness)
                    text_width, text_height = text_size

                    # Draw red background rectangle above face
                    cv2.rectangle(uploaded_image_bgr, (left, top - text_height - 10), (left + text_width + 10, top),
                                  (0, 0, 255), cv2.FILLED)

                    # Put the "Unknown" text over the rectangle
                    cv2.putText(uploaded_image_bgr, unknown_text, (left + 5, top - 5), font, font_scale,
                                (255, 255, 255), thickness)

            # Save the image with rectangles drawn
            drawn_filename = f"detected_{uuid.uuid4().hex}.jpg"  # Create unique filename using uuid
            drawn_image_path = os.path.join(settings.MEDIA_ROOT, drawn_filename)  # Path to save drawn image
            cv2.imwrite(drawn_image_path, uploaded_image_bgr)  # Write (save) the image

            drawn_image_url = settings.MEDIA_URL + drawn_filename  # Get URL to access the saved image

            # Build the context to send to template
            if matched_profiles:
                context = {
                    'photo_url': drawn_image_url,  # Show image with drawings
                    'matched_profiles': matched_profiles  # Show matched profiles
                }
            else:
                context = {
                    'photo_url': drawn_image_url,
                    'error': 'No matching profiles found for the uploaded face(s).'  # No match found
                }

        else:
            # No face detected
            context = {
                'error': 'No face detected in the uploaded image.'
            }

        return render(request, 'upload_photo.html', context)  # Render template with context

    # If not POST, just render the upload page
    return render(request, 'upload_photo.html')

# View for performing live face recognition
def LiveRecognition(request):
    """
        Handles live facial recognition based on a webcam image captured and sent by the client. This view function
        processes POST requests containing the captured image data in base64 format, performs facial recognition,
        and compares the detected faces with known profiles in the database.

        The process is as follows:
        - The image is captured from the webcam and sent as base64-encoded data.
        - The image is decoded and saved temporarily.
        - Facial recognition is performed on the uploaded image, and the detected faces are compared against the
          known profiles' images stored in the database.
        - Green rectangles are drawn around matched faces, and red rectangles are drawn around unmatched faces.
        - The result (modified image with rectangles) is saved, and either matched profiles or an error message is
          displayed to the user.

        POST data is expected to contain:
        - 'captured_image': The base64-encoded image from the client's webcam.

        If faces are detected, they are compared with known profiles, and the result (image with rectangles and
        matched profiles) is returned to the template. Activity logs are created for successful face recognitions.

        If no faces are detected, an error message is displayed.

        Args:
        request: The HTTP request object containing the captured image data.

        Returns:
        A rendered template with the modified image containing rectangles around recognized faces, or an error message
        if no faces were detected or no matches were found in the database.
"""
    matched_profiles = []  # List to store all matched profiles

    # Get the captured image data from POST request
    image_data = request.POST.get('captured_image')

    if image_data:
        # Split the base64 encoded image into format and data
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]  # Extract the file extension (like jpg or png)

        # Generate a unique filename using timestamp
        file_name = f"webcam_capture_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        temp_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Path to save the image

        # Save the decoded base64 image into a file
        with open(temp_path, 'wb') as f:
            f.write(base64.b64decode(imgstr))

        # Load the saved image for processing
        rgb_image = face_recognition.load_image_file(temp_path)
        face_locations = face_recognition.face_locations(rgb_image)  # Detect face locations

        # If no face is found, render page with error
        if not face_locations:
            return render(request, 'live_recognition.html', {
                'photo': settings.MEDIA_URL + file_name,
                'error': 'No face detected.'
            })

        # Encode the faces found in the uploaded image
        encodings = face_recognition.face_encodings(rgb_image, face_locations)

        known_encodings = []  # List to store known encodings from database
        known_profiles = []  # List to store corresponding profiles

        # Load all user profiles from the database
        for profile in UserProfile.objects.all():
            profile_image_path = os.path.join(settings.MEDIA_ROOT, profile.image.name)  # Path of stored profile image
            if os.path.exists(profile_image_path):
                profile_image = face_recognition.load_image_file(profile_image_path)  # Load profile image
                profile_encodings = face_recognition.face_encodings(profile_image)
                if profile_encodings:
                    known_encodings.append(profile_encodings[0])  # Store first encoding
                    known_profiles.append(profile)  # Store the profile

        # Convert RGB image to BGR for OpenCV (cv2) drawing
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        # Settings for text font
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        matched_profiles = []  # Initialize matched profiles list

        # Check if any known encodings are available
        if known_encodings:
            # Iterate over each face detected
            for i, input_encoding in enumerate(encodings):
                matches = face_recognition.compare_faces(known_encodings, input_encoding,
                                                         tolerance=0.55)  # Compare faces
                face_distances = face_recognition.face_distance(known_encodings, input_encoding)  # Get distances

                (top, right, bottom, left) = face_locations[i]  # Get face coordinates

                # If there are matches
                if matches and np.any(matches):
                    best_match_index = np.argmin(face_distances)  # Find the best match index

                    # If best match is valid
                    if matches[best_match_index]:
                        matched_profile = known_profiles[best_match_index]
                        matched_profiles.append(matched_profile)  # Add to matched list

                        # Draw green rectangle for matched face
                        cv2.rectangle(bgr_image, (left, top), (right, bottom), (0, 255, 0), 2)

                        # Draw background rectangle for matched profile name
                        name_text = matched_profile.name
                        text_size, _ = cv2.getTextSize(name_text, font, font_scale, thickness)
                        text_width, text_height = text_size
                        cv2.rectangle(bgr_image, (left, top - text_height - 10), (left + text_width + 10, top),
                                      (0, 255, 0), cv2.FILLED)

                        # Draw profile name text
                        cv2.putText(bgr_image, name_text, (left + 5, top - 5), font, font_scale, (0, 0, 0), thickness)

                        # Log the successful recognition into ActivityLog
                        ActivityLog.objects.create(
                            user=request.user,
                            action=f"Live recognition success for {matched_profile.name}"
                        )
                    else:
                        # If no good match, draw red rectangle for unknown face
                        cv2.rectangle(bgr_image, (left, top), (right, bottom), (0, 0, 255), 2)

                        # Draw background rectangle for "Unknown" label
                        unknown_text = "Unknown"
                        text_size, _ = cv2.getTextSize(unknown_text, font, font_scale, thickness)
                        text_width, text_height = text_size
                        cv2.rectangle(bgr_image, (left, top - text_height - 10), (left + text_width + 10, top),
                                      (0, 0, 255), cv2.FILLED)

                        # Draw "Unknown" text
                        cv2.putText(bgr_image, unknown_text, (left + 5, top - 5), font, font_scale, (255, 255, 255),
                                    thickness)

                else:
                    # If no matches found at all, draw red rectangle for unknown face
                    cv2.rectangle(bgr_image, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw background rectangle for "Unknown" label
                    unknown_text = "Unknown"
                    text_size, _ = cv2.getTextSize(unknown_text, font, font_scale, thickness)
                    text_width, text_height = text_size
                    cv2.rectangle(bgr_image, (left, top - text_height - 10), (left + text_width + 10, top), (0, 0, 255),
                                  cv2.FILLED)

                    # Draw "Unknown" text
                    cv2.putText(bgr_image, unknown_text, (left + 5, top - 5), font, font_scale, (255, 255, 255),
                                thickness)

        # Generate a new filename for the processed image
        drawn_filename = f"drawn_{uuid.uuid4().hex}.jpg"
        drawn_path = os.path.join(settings.MEDIA_ROOT, drawn_filename)

        # Save the image with rectangles and labels drawn
        cv2.imwrite(drawn_path, bgr_image)

        # Build the context to render the page
        if matched_profiles:
            context = {
                'photo': settings.MEDIA_URL + drawn_filename,  # URL for drawn image
                'profiles': matched_profiles,  # List of matched profiles
            }
        else:
            context = {
                'photo': settings.MEDIA_URL + drawn_filename,  # URL for drawn image
                'error': 'No matching faces found in database.'  # Error message
            }

        # Render the live recognition page with results
        return render(request, 'live_recognition.html', context)

    # If no image data submitted, simply render the page
    return render(request, 'live_recognition.html')

# > > > > > > > Home Page View Function End < < < < < < <

# > > > > > > > Dashboard Views Functions Start < < < < < < <

@login_required
# View to display the admin dashboard
def Dashboard(request):
    """
        Handles the dashboard view for admin users. This view checks if the logged-in user is a superuser (admin),
        and if so, it displays a dashboard with key metrics and recent activities. If the user is not a superuser,
        they are redirected to the home page with an error message.

        Key features of the dashboard:
        - Displays total number of registered users.
        - Displays the total number of active user profiles.
        - Displays the total number of successful face recognitions logged in activity records.
        - Displays the 10 most recent activity logs, including user information.

        If the logged-in user is not a superuser, they will be denied access to the dashboard.

        Args:
        request: The HTTP request object containing user session information.

        Returns:
        A rendered template of the dashboard page containing the context data:
        - 'total_users': Total number of registered users.
        - 'active_profiles': Total number of user profiles created.
        - 'total_recognitions': Total number of successful face recognitions.
        - 'recent_activities': The 10 most recent activity logs.
        """
    # Check if the logged-in user is a superuser (admin)
    if not request.user.is_superuser:
        # If not, show an error message and redirect to the home page
        messages.error(request, "You cannot access that page.")
        return redirect('home')

    # Get the 10 most recent activity logs along with user info
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]

    # Prepare context data for the dashboard template
    context = {
        'total_users': User.objects.count(),  # Total number of registered users
        'active_profiles': UserProfile.objects.count(),  # Total user profiles created
        'total_recognitions': ActivityLog.objects.filter(action__icontains='Recognition success').count(),  # Total successful face recognitions
        'recent_activities': recent_activities  # Recent activities (latest 10)
    }

    # Render the dashboard page with context data
    return render(request, 'dashboard.html', context)

# View to display the list of all users with pagination
def UserDetailsPage(request):
    """
        Handles the display of user details with pagination. This view fetches all user objects from the database,
        paginates them to show 5 users per page, and renders the user details page with the paginated user data.

        If the request contains a page number in the query string (e.g., ?page=2), the corresponding set of users
        will be displayed. If no page number is provided, it will show the first page of users.

        Args:
        request: The HTTP request object containing query parameters for pagination.

        Returns:
        A rendered template 'userdetails.html' with the paginated user data (page_obj).
        The template will display the list of users for the current page and allow navigation through the paginated list.
        """
    # Get all user objects from the database
    user_list = User.objects.all()

    # Paginate the user list - display 5 users per page
    paginator = Paginator(user_list, 5)

    # Get the current page number from the query parameters (e.g., ?page=2)
    page_number = request.GET.get('page')

    # Get the users for the current page
    page_obj = paginator.get_page(page_number)

    # Render the 'userdetails.html' template with the paginated user data
    return render(request, 'userdetails.html', {'page_obj': page_obj})

# View to handle updating a user's information
def UpdateUser(request, user_id):
    """
        Handles the updating of a user's details. This view allows updating a user's username and email,
        but prevents editing of superuser accounts.

        If the request method is POST, the user's details (username and email) are updated with the values
        submitted in the form. If the request method is GET, the user's existing details are displayed in
        a form for editing.

        Args:
        request: The HTTP request object, which can contain a POST or GET request.
        user_id: The ID of the user whose details need to be updated.

        Returns:
        - If the request method is POST, the updated user details are saved and the user is redirected to
          the 'user_details' page.
        - If the request method is GET, the 'update_user.html' template is rendered with the current user
          details for editing.
        - If the user is a superuser, an HTTPForbidden response is returned with an appropriate message.
        """
    # Fetch the user object from the database based on the given user ID
    user = User.objects.get(id=user_id)

    # Prevent editing if the user is a superuser
    if user.is_superuser:
        return HttpResponseForbidden("You cannot edit a superuser.")

    # If the request is a POST method, update the user's details
    if request.method == 'POST':
        # Get updated values from the form submission
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')

        # Save the updated user information to the database
        user.save()

        # Redirect to the user details page after successful update
        return redirect('user_details')

    # For GET requests, render the update user form with existing user data
    return render(request, 'update_user.html', {'user': user})

# View to delete a user from the system
def DeleteUser(request, user_id):
    """
        Handles the deletion of a user from the database. This view allows the deletion of a user, but
        prevents deletion of superuser accounts. The user is only deleted after a confirmation via a POST request.

        If the request method is POST, the user is deleted from the database and the user is redirected
        to the user details page. If the request method is GET, a confirmation page is rendered to ask
        the user for confirmation before deletion.

        Args:
        request: The HTTP request object, which can contain a POST or GET request.
        user_id: The ID of the user to be deleted.

        Returns:
        - If the request method is POST, the user is deleted and the user is redirected to the 'user_details' page.
        - If the request method is GET, the 'delete_user.html' template is rendered, asking for confirmation before deletion.
        - If the user is a superuser, an HTTPForbidden response is returned with an appropriate message.
        """
    # Retrieve the user object from the database using the provided user ID
    user = User.objects.get(id=user_id)

    # Prevent deletion if the user is a superuser
    if user.is_superuser:
        return HttpResponseForbidden("You cannot delete a superuser.")

    # If the request method is POST, proceed with deletion
    if request.method == 'POST':
        # Delete the user from the database
        user.delete()

        # Redirect to the user details page after successful deletion
        return redirect('user_details')

    # If the request method is GET, render a confirmation page before deletion
    return render(request, 'delete_user.html', {'user': user})

@login_required
# View to create a new user profile (accessible only by superusers)
def create_profile(request):
    """
        Handles the creation of a user profile by superusers. The function checks if the user is a superuser
        before allowing access to the profile creation page. Upon form submission, it saves the user profile
        and associated additional images.

        If the request method is POST, the profile form and any additional images are processed and saved.
        After a successful save, the user is redirected to the profile list page. If the request method is GET,
        an empty profile creation form is displayed.

        Args:
        request: The HTTP request object, which can contain a POST or GET request.

        Returns:
        - On POST request: Redirects to the 'profile_list' page upon successful creation of the profile.
        - On GET request: Renders the 'create_profile.html' template with an empty form.
        - If the user is not a superuser: Displays an error message and redirects to the home page.
        """
    # Restrict access: only superusers can create profiles
    if not request.user.is_superuser:
        messages.error(request, "You cannot access that page.")
        return redirect('home')

    # Handle POST request when form is submitted
    if request.method == 'POST':
        # Bind submitted data and files to the form
        form = UserProfileForm(request.POST, request.FILES)

        # Get list of uploaded additional images
        files = request.FILES.getlist('additional_images')

        # Validate the form input
        if form.is_valid():
            # Save the main profile
            profile = form.save()

            # Save each additional image and associate it with the profile
            for file in files:
                ProfileImage.objects.create(profile=profile, image=file)

            # Redirect to the profile list after successful creation
            return redirect('profile_list')

    else:
        # If GET request, display an empty form
        form = UserProfileForm()

    # Render the form on the template
    return render(request, 'create_profile.html', {'form': form})

# Class-based view to display a list of user profiles (accessible only to superusers)
class ProfileListView(UserPassesTestMixin, ListView):
    """
        A class-based view that displays a list of user profiles, ordered by creation date. The view is
        restricted to superusers only. It supports search functionality, allowing users to search for profiles
        by name. If no search term is provided, all profiles are displayed.

        Attributes:
            model: The model to use for querying the profiles (`UserProfile`).
            template_name: The template to render the view (`profile_list.html`).
            context_object_name: The context variable name that will contain the list of profiles (`profiles`).
            ordering: The default ordering of profiles (by `created_at`, newest first).

        Methods:
            test_func: Checks whether the user is a superuser before allowing access.
            handle_no_permission: Redirects users without permission to access the page with an error message.
            get_queryset: Retrieves the list of profiles, supporting a search query to filter profiles by name.
            get_context_data: Passes additional context, including the current search query, to the template.
        """
    model = UserProfile  # The model this view will display
    template_name = 'profile_list.html'  # Template to render the view
    context_object_name = 'profiles'  # The name of the list in the template context
    ordering = ['-created_at']  # Order profiles by creation date (newest first)

    # Restrict access to superusers only
    def test_func(self):
        return self.request.user.is_superuser

    # Redirect with an error message if user is not authorized
    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        return redirect('home')

    # Custom queryset to support search functionality
    def get_queryset(self):
        query = self.request.GET.get('q', '')  # Get the search term from the query parameters
        if query:
            # Filter profiles by name if a search term is provided
            return UserProfile.objects.filter(name__icontains=query).order_by('-created_at')
        # Return all profiles if no search term
        return UserProfile.objects.all().order_by('-created_at')

    # Pass additional context to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include the current search query in the context for display or form prefill
        context['search_query'] = self.request.GET.get('q', '')
        return context

# Class-based view to handle displaying additional images for a user profile
class ProfileImagesView(View):
    """
        A class-based view to handle the display of a user profile and its associated additional images.
        The view responds to GET requests and retrieves the specified profile and its additional images
        from the database. It then renders the profile images on a template.

        Methods:
            get: Handles GET requests. Fetches the user profile by primary key (`pk`) and retrieves
                 all additional images associated with that profile. Renders the 'profile_images.html'
                 template with the profile and its images.
        """
    # Handle GET requests to display the profile and its additional images
    def get(self, request, pk):
        # Fetch the user profile object based on the primary key (pk)
        profile = get_object_or_404(UserProfile, pk=pk)

        # Retrieve all additional images related to this profile
        additional_images = profile.additional_images.all()

        # Render the 'profile_images.html' template, passing the profile and images as context
        return render(request, 'profile_images.html', {'profile': profile, 'additional_images': additional_images})

# Class-based view to handle deleting a user profile
class ProfileDeleteView(UserPassesTestMixin, View):
    """
        A class-based view to handle the deletion of a user profile. Only superusers are authorized to
        delete profiles. If the user is not a superuser, they will be redirected with an error message.
        Upon successful deletion, a success message is displayed, and the user is redirected to the profile
        list page.

        Methods:
            test_func: Checks if the current user is a superuser. Only superusers can delete profiles.
            handle_no_permission: Redirects the user with an error message if they are not a superuser.
            post: Handles POST requests to delete a profile based on the provided primary key (`pk`).
                  The profile is deleted, and a success message is displayed before redirecting to the profile list.
        """
    # Check if the current user is a superuser before allowing profile deletion
    def test_func(self):
        # Only allow superusers to delete profiles
        return self.request.user.is_superuser

    # If the user is not authorized to delete, redirect with an error message
    def handle_no_permission(self):
        # Display an error message if the user does not have permission
        messages.error(self.request, "You do not have permission to delete profiles.")
        return redirect('profile_list')

    # Handle POST request to delete a profile
    def post(self, request, pk, *args, **kwargs):
        # Fetch the user profile based on the primary key (pk)
        profile = get_object_or_404(UserProfile, pk=pk)

        # Save the profile name before deletion for confirmation message
        profile_name = profile.name

        # Delete the profile
        profile.delete()

        # Show a success message indicating the profile has been deleted
        messages.success(request, f'Profile "{profile_name}" has been deleted.')

        # Redirect back to the profile list page
        return redirect('profile_list')

# > > > > > > > Deshboard View Function End < < < < < < <