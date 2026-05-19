class AICoach {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');

        this.ws = null;
        this.lastSendTime = 0;
        this.prevLandmarks = null;
        this.prevMovement = 0;
        this.wsReconnectAttempts = 0;

        this.timerInterval = null;
        this.secondsElapsed = 0;

        this.isActive = false;
        this.isPaused = false;
        this.modelsLoaded = false;
        this.shouldSave = true; 

        this.setupButtons();
        this.initPose();
    }

    setupButtons() {
        document.getElementById('startBtn').onclick = () => this.startSession();
        document.getElementById('pauseBtn').onclick = () => this.togglePause();
        document.getElementById('stopBtn').onclick = () => this.finishSession(true);
        document.getElementById('exitBtn').onclick = () => {
            if (confirm("Вийти без збереження?")) {
                this.finishSession(false);
            }
        };
    }

    startTimer() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        this.timerInterval = setInterval(() => {
            if (!this.isPaused) {
                this.secondsElapsed++;
                const mins = Math.floor(this.secondsElapsed / 60).toString().padStart(2, '0');
                const secs = (this.secondsElapsed % 60).toString().padStart(2, '0');
                document.getElementById('timer').innerText = `${mins}:${secs}`;
            }
        }, 1000);
    }

    updateUI(status) {
        document.getElementById('sessionStatus').innerText = status;
    }

    startSession() {
        this.isActive = true;
        this.isPaused = false;
        this.secondsElapsed = 0;
        this.shouldSave = true;
        this.initWebSocket();
        this.startTimer();

        document.getElementById('startBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;
        this.updateUI('Recording');
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        this.updateUI(this.isPaused ? 'Paused' : 'Recording');
        document.getElementById('pauseBtn').innerText = this.isPaused ? 'Resume' : 'Pause';
    }

    async finishSession(save) {
        this.shouldSave = save;
        if (this.ws) {

            this.ws.send(JSON.stringify({ type: save ? 'end_session' : 'cancel_session' }));

            if (!save) {
                this.ws.close();
                window.location.href = '/dashboard/';
            }
        } else {
            window.location.href = '/dashboard/';
        }
        clearInterval(this.timerInterval);
    }

    async initWebSocket() {
        const wsUrl = `ws://${window.location.host}/ws/coach/`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onmessage = (e) => {
            const data = JSON.parse(e.data);

            if (data.type === 'live_update') {
                const scoreEl = document.getElementById('liveScore');
                if (scoreEl) {
                    const score = Math.round(data.score);
                    scoreEl.innerText = `Score: ${score}%`;
                    scoreEl.style.color = score > 60 ? 'var(--success)' :
                        score > 20 ? 'var(--warning)' : 'var(--danger)';
                }

                const list = document.getElementById('problemsList');
                if (list) {
                    const existingProblems = Array.from(list.querySelectorAll('.problem-item')).map(el => el.innerText);
                    const newProblems = data.problems;
                    if (JSON.stringify(existingProblems.sort()) === JSON.stringify(newProblems.sort())) {
                        return;
                    }

                    list.innerHTML = '';
                    if (newProblems.length === 0) {
                        list.innerHTML = '<p class="no-problems">Помилок не виявлено. Так тримати!</p>';
                    } else {
                        newProblems.forEach(prob => {
                            const div = document.createElement('div');
                            div.className = 'problem-item';
                            div.innerText = prob;
                            list.appendChild(div);
                        });
                    }
                }
            }

            if (data.type === 'final_score') {
                const finalScore = Math.round(data.score);
                alert(`Сесію завершено! Ваш результат: ${finalScore}%`);
                window.location.href = '/dashboard/';
            }
        };

        this.ws.onclose = () => {
            clearInterval(this.timerInterval);
        };
    }

    initPose() {
        this.pose = new Pose({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
        });
        this.pose.setOptions({ modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
        this.pose.onResults(this.onResults.bind(this));

        try {
            const camera = new Camera(this.video, {
                onFrame: async () => { 
                    if (this.pose) {
                        await this.pose.send({ image: this.video }); 
                    }
                },
                width: 640, 
                height: 480
            });

            camera.start();
            console.log('Camera started successfully');
        } catch (error) {
            console.error('Camera initialization error:', error);
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.innerHTML = `
                    <div style="text-align: center; color: #ef4444;">
                        <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">Помилка камери</p>
                        <p style="margin: 0.5rem 0;">${error.message}</p>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #f59e0b;">
                            Переконайтесь, що:
                        </p>
                        <ul style="text-align: left; display: inline-block; color: #f59e0b;">
                            <li>Ви дозволили доступ до камери</li>
                            <li>Камера не використовується іншою програмою</li>
                            <li>Браузер має дозвіл на доступ до камери</li>
                        </ul>
                    </div>
                `;
            }
            throw error;
        }
    }

    onResults(results) {
        if (!this.modelsLoaded) {
            this.modelsLoaded = true;
            document.getElementById('loadingOverlay').classList.add('hidden');
        }

        this.ctx.save();
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(results.image, 0, 0, this.canvas.width, this.canvas.height);

        if (results.poseLandmarks) {
            drawConnectors(this.ctx, results.poseLandmarks, POSE_CONNECTIONS, { color: '#00FF00', lineWidth: 2 });
            if (this.isActive && !this.isPaused) {
                const now = Date.now();
                if (now - this.lastSendTime >= 200) {
                    const features = this.extractFeatures(results.poseLandmarks);
                    if (features && this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify(features));
                        this.lastSendTime = now;
                    }
                }
            }
        }
        this.ctx.restore();
    }

    extractFeatures(landmarks) {
        if (!landmarks) return null;
        const leftWrist = landmarks[15], rightWrist = landmarks[16];
        const leftShoulder = landmarks[11], rightShoulder = landmarks[12];
        const nose = landmarks[0], leftEar = landmarks[7], rightEar = landmarks[8];

        const shoulderWidth = Math.hypot(leftShoulder.x - rightShoulder.x, leftShoulder.y - rightShoulder.y);

        const wristDistance = Math.hypot(leftWrist.x - rightWrist.x, leftWrist.y - rightWrist.y);

        const hands_crossed = wristDistance < (shoulderWidth * 0.3) ? 1 : 0;
        const aspect = this.canvas.width / this.canvas.height;
        let movement = 0;
        if (this.prevLandmarks) {
            movement = Math.hypot((leftWrist.x - this.prevLandmarks[15].x) * aspect, leftWrist.y - this.prevLandmarks[15].y);
        }
        const symmetry = Math.abs(leftShoulder.y - rightShoulder.y);
        const eye_contact = (nose.x > Math.min(leftEar.x, rightEar.x) && nose.x < Math.max(leftEar.x, rightEar.x)) ? 1 : 0;
        const jerk = Math.abs(movement - this.prevMovement);
        this.prevLandmarks = landmarks; this.prevMovement = movement;
        return { movement, hands_crossed, eye_contact, symmetry, jerk };
    }

    cleanup() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close();
        }
        if (this.pose) {
            this.pose.close();
        }
        console.log('AICoach cleaned up');
    }

}

document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('input_video');
    const canvas = document.getElementById('output_canvas');
    if (video && canvas) window.coach = new AICoach(video, canvas);
});