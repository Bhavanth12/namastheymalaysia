// App logic for interactions like the custom cursor and scroll-to-top button
document.addEventListener('DOMContentLoaded', () => {

    // --- Custom Cursor ---
    const cursorDot = document.querySelector('.cursor-dot');
    const cursorOutline = document.querySelector('.cursor-outline');

    if(cursorDot && cursorOutline) {
        window.addEventListener('mousemove', (e) => {
            const posX = e.clientX;
            const posY = e.clientY;

            cursorDot.style.left = `${posX}px`;
            cursorDot.style.top = `${posY}px`;
            
            cursorOutline.animate({
                left: `${posX}px`,
                top: `${posY}px`
            }, { duration: 150, fill: "forwards" });
        });

        document.addEventListener('mouseover', (e) => {
            if(e.target.tagName.toLowerCase() === 'a' || e.target.tagName.toLowerCase() === 'button' || e.target.closest('.activity-item')) {
                cursorOutline.style.width = '60px';
                cursorOutline.style.height = '60px';
                cursorOutline.style.backgroundColor = 'rgba(240, 106, 47, 0.1)';
                cursorOutline.style.borderColor = 'transparent';
            }
        });

        document.addEventListener('mouseout', (e) => {
            if(e.target.tagName.toLowerCase() === 'a' || e.target.tagName.toLowerCase() === 'button' || e.target.closest('.activity-item')) {
                cursorOutline.style.width = '36px';
                cursorOutline.style.height = '36px';
                cursorOutline.style.backgroundColor = 'transparent';
                cursorOutline.style.borderColor = '#f06a2f';
            }
        });
    }

    // --- Scroll to Top Button ---
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if(scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });
    }

    // --- Scroll Animations ---
    const animatedElements = document.querySelectorAll('.activity-item, .post-item, .sect-title-orange');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(el => observer.observe(el));

    // --- Cultural Quiz Logic ---
    const quizData = [
        {
            question: "Which iconic building in Kuala Lumpur was once the tallest in the world?",
            options: ["KL Tower", "Petronas Twin Towers", "Merdeka 118", "Sultan Abdul Samad Building"],
            correct: 1
        },
        {
            question: "What is considered the national dish of Malaysia?",
            options: ["Char Kway Teow", "Laksa", "Nasi Lemak", "Roti Canai"],
            correct: 2
        },
        {
            question: "Which major festival features the carrying of intricate 'kavadis'?",
            options: ["Hari Raya Aidilfitri", "Thaipusam", "Deepavali", "Wesak Day"],
            correct: 1
        },
        {
            question: "Which Malaysian state is famous for its historic UNESCO-listed George Town?",
            options: ["Penang", "Melaka", "Sarawak", "Sabah"],
            correct: 0
        },
        {
            question: "The traditional Kadazan-Dusun harvest festival celebrated in Sabah is called:",
            options: ["Gawai Dayak", "Kaamatan", "Rainforest World Music Festival", "Mooncake Festival"],
            correct: 1
        }
    ];

    let currentQuestionIndex = 0;
    let score = 0;

    const quizContainer = document.getElementById('quizContainer');
    if(quizContainer) {
        const questionEl = document.getElementById('quizQuestion');
        const optionsEl = document.getElementById('quizOptions');
        const progressEl = document.getElementById('quizProgress');
        const contentEl = document.getElementById('quizContent');
        const resultEl = document.getElementById('quizResult');
        const scoreTextEl = document.getElementById('quizScoreText');
        const retryBtn = document.getElementById('retryQuizBtn');

        function loadQuestion() {
            const currentQuizData = quizData[currentQuestionIndex];
            questionEl.innerText = currentQuizData.question;
            optionsEl.innerHTML = '';
            
            currentQuizData.options.forEach((option, index) => {
                const btn = document.createElement('button');
                btn.classList.add('quiz-btn');
                btn.innerText = option;
                btn.addEventListener('click', () => selectAnswer(index, btn));
                optionsEl.appendChild(btn);
            });
            
            progressEl.innerText = `Question ${currentQuestionIndex + 1} / ${quizData.length}`;
        }

        function selectAnswer(selectedIndex, btnElement) {
            const correctIndex = quizData[currentQuestionIndex].correct;
            const isCorrect = (selectedIndex === correctIndex);
            
            // Disable all buttons once an answer is chosen
            const allBtns = optionsEl.querySelectorAll('.quiz-btn');
            allBtns.forEach(b => {
                b.disabled = true;
                b.style.cursor = 'default';
            });

            if(isCorrect) {
                btnElement.classList.add('correct');
                score++;
            } else {
                btnElement.classList.add('wrong');
                // Highlight the correct one
                allBtns[correctIndex].classList.add('correct');
            }

            // Wait a short moment then load next
            setTimeout(() => {
                currentQuestionIndex++;
                if (currentQuestionIndex < quizData.length) {
                    loadQuestion();
                } else {
                    showResult();
                }
            }, 1200);
        }

        function showResult() {
            contentEl.style.display = 'none';
            resultEl.style.display = 'block';
            scoreTextEl.innerText = `You scored ${score} out of ${quizData.length}!`;
        }

        retryBtn.addEventListener('click', () => {
            currentQuestionIndex = 0;
            score = 0;
            resultEl.style.display = 'none';
            contentEl.style.display = 'block';
            loadQuestion();
        });

        // Initialize first question
        loadQuestion();
    }

    // --- Feedback Form Logic ---
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent page reload
            
            const formData = new FormData(feedbackForm);
            
            // Show loading state
            const submitBtn = feedbackForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerText;
            submitBtn.innerText = 'Submitting...';
            submitBtn.disabled = true;

            const responseMsg = document.getElementById('feedbackResponse');
            
            // Submit to Formspree
            fetch('https://formspree.io/f/mkoqpwgq', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (response.ok) {
                    // Show thank you message
                    responseMsg.style.display = 'block';
                    responseMsg.style.color = 'var(--accent-green)';
                    responseMsg.innerText = 'Thank you for your feedback! It helps us improve.';
                    
                    // Reset the form
                    feedbackForm.reset();
                } else {
                    throw new Error('Form submission failed');
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                responseMsg.style.display = 'block';
                responseMsg.style.color = '#e74c3c'; // Red for error
                responseMsg.innerText = 'Oops! There was a problem submitting your form. Please try again.';
            })
            .finally(() => {
                // Restore button state
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
                
                // Hide message after 5 seconds
                setTimeout(() => {
                    responseMsg.style.display = 'none';
                }, 5000);
            });
        });
    }

});
