document.addEventListener("DOMContentLoaded", function () {
    // Initialize all modals
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        new bootstrap.Modal(modal);
    });

    // Handle profile image click to toggle additional images
    document.querySelectorAll(".profile-image img").forEach(img => {
        img.addEventListener("click", function () {
            let profileId = this.getAttribute("data-profile-id");
            let additionalImagesDiv = document.getElementById(`additional-images-${profileId}`);

            if (additionalImagesDiv) {
                // Toggle visibility
                if (additionalImagesDiv.style.display === "none" || additionalImagesDiv.style.display === "") {
                    additionalImagesDiv.style.display = "block";
                } else {
                    additionalImagesDiv.style.display = "none";
                }
            }
        });
    });
});

