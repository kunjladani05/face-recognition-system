document.addEventListener('DOMContentLoaded', () => {
    // Parallax effect for mesh overlay
    document.addEventListener('mousemove', (e) => {
        const mesh = document.querySelector('.mesh-overlay');
        const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
        const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
        mesh.style.transform = `translate(${xAxis}px, ${yAxis}px) scale(1.1)`;
    });

    // Animate elements on scroll
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    };

    const observer = new IntersectionObserver(animateOnScroll, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observe cards for animation
    document.querySelectorAll('.info-card, .feature, .use-case-card').forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'all 0.6s ease-out';
        observer.observe(element);
    });

    // Add 3D tilt effect to feature cards
    document.querySelectorAll('.feature').forEach(feature => {
        feature.addEventListener('mousemove', (e) => {
            const rect = feature.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const xc = rect.width / 2;
            const yc = rect.height / 2;

            const dx = x - xc;
            const dy = y - yc;

            feature.style.transform = `perspective(1000px) rotateX(${dy / -20}deg) rotateY(${dx / 20}deg) translateZ(10px)`;
            feature.style.transition = 'transform 0.1s ease';
        });

        feature.addEventListener('mouseleave', () => {
            feature.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
            feature.style.transition = 'transform 0.3s ease';
        });
    });

    // Add smooth scrolling for better user experience
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});