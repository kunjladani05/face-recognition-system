from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ActivityLog Model: Stores user activity logs
# Model to log activities performed by users (e.g., login, profile update)
class ActivityLog(models.Model):
    """
        Model to track user activities in the system.

        Each log entry is associated with a specific user, capturing the action
        performed (e.g., login, logout, profile update). The related user is
        deleted automatically when the user is removed, as specified by the
        'on_delete=models.CASCADE' constraint.

        Attributes:
            user: ForeignKey to the User model, linking each log entry to a specific user.
            action: A description of the action performed by the user (e.g., login, logout).
            timestamp: Automatically set to the current date and time when the log is created.
    """
    # ForeignKey to link each activity to a specific user
    # If a User is deleted, their associated activity logs are also deleted due to 'on_delete=models.CASCADE'
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Action performed by the user (e.g., login, logout, profile update)
    action = models.CharField(max_length=255)

    # Details of the action, optional to provide more context
    details = models.TextField(blank=True, null=True)

    # Timestamp when the activity was logged, automatically set when a new record is created
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order the activity logs by timestamp in descending order (newest first)
        ordering = ['-timestamp']

    def __str__(self):
        # String representation of the ActivityLog, showing the user's username and the action performed
        return f"{self.user.username} - {self.action}"


def user_additional_images_path(instance, filename):
    """
        Store additional images in a unique folder based on user email.
    """
    return f'profile_images/additional/{instance.profile.email}/{filename}'

# UserProfile Model: Stores user profile details
class UserProfile(models.Model):
    """
        Model to store user profile details.

        This model is used to store various information about users, including
        their profile image, personal details (name, phone number, email, address),
        date of birth, age, gender, height, and weight. Additionally, it tracks the
        creation and last update timestamps for each profile.

        Attributes:
            GENDER_CHOICES (list): Options for gender ('M' for Male, 'F' for Female, 'O' for Other).
            image (ImageField): Profile image of the user, stored in 'profile_images/' directory.
            name (CharField): Name of the user, with a maximum length of 100 characters.
            phone_number (CharField): User's phone number, stored as a string to handle different formats.
            email (EmailField): Unique email address of the user.
            address (TextField): Free-text address field for storing the user's address.
            date_of_birth (DateField): User's date of birth.
            age (IntegerField): User's age, validated to be between 0 and 150 years.
            gender (CharField): Gender of the user, represented as a single character ('M', 'F', or 'O').
            height (DecimalField): User's height in centimeters, stored with two decimal places.
            weight (DecimalField): User's weight in kilograms, stored with two decimal places.
            created_at (DateTimeField): Timestamp when the profile was created (auto-generated).
            updated_at (DateTimeField): Timestamp when the profile was last updated (auto-generated).

        Methods:
            __str__: Returns the user's name as a string representation of the profile.
    """
    objects = None  # This should be removed; it overrides the default model manager and prevents queries

    # Gender choices for users
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    image = models.ImageField(upload_to='profile_images/')  # Stores profile images in 'profile_images/' directory
    name = models.CharField(max_length=100)  # Stores user's name with a maximum length of 100 characters
    phone_number = models.CharField(max_length=15)  # Stores phone number (as a string to accommodate different formats)
    email = models.EmailField(unique=True)  # Stores email; must be unique to prevent duplicates
    address = models.TextField()  # Stores user's address as free text
    date_of_birth = models.DateField()  # Stores date of birth

    # Stores age with validation (age must be between 0 and 150)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])

    # Stores gender as a single character (M, F, or O)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # Stores height and weight with decimal precision
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm")  # Example: 175.50 cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")  # Example: 70.25 kg

    created_at = models.DateTimeField(auto_now_add=True)  # Automatically sets timestamp when profile is created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates timestamp when profile is modified

    def __str__(self):
        return self.name  # Returns the user's name when printing the object


# Model to represent additional images associated with a user profile
class ProfileImage(models.Model):
    """
        Model to store additional images for a user profile.

        This model is used to store multiple images associated with a user profile.
        It allows users to upload additional images that are linked to their profile.
        The images are stored in a directory unique to each user's email, using the
        `user_additional_images_path` function for organizing the storage path.

        Attributes:
            profile (ForeignKey): A link to the `UserProfile` model, which represents the user to whom the image belongs.
                If the associated `UserProfile` is deleted, the related images are also deleted due to the 'on_delete=models.CASCADE' option.
            image (ImageField): The uploaded image, which is stored according to the path defined in the `user_additional_images_path` function.

        Methods:
            __str__: Returns the path of the image file as a string representation of the image object.
    """
    # ForeignKey to link the image to a specific UserProfile
    # If a UserProfile is deleted, the associated images are also deleted due to 'on_delete=models.CASCADE'
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='additional_images')

    # Image field to store the image file. The images will be uploaded to a path defined by the 'user_additional_images_path' function.
    image = models.ImageField(upload_to=user_additional_images_path)
