// [핵심 1] seekTo 함수를 전역으로 뺌 (HTML onclick에서 쓰려면 여기 있어야 함)
function seekTo(seconds, element) {
    const video = document.getElementById('lecture');
    if (video) {
        video.currentTime = Number(seconds);
        video.play();
    } else {
        console.error("비디오 태그를 찾을 수 없습니다.");
    }
}

// [핵심 2] 그래프 함수도 전역으로 뺌
function drawEmpathyGraph(data) {
    const ctx = document.getElementById('questionChart');
    if (!ctx) return;

    // 데이터가 없어도 그래프 틀은 나오게 처리
    const groupedData = {};
    if (data && data.length > 0) {
        data.forEach(item => {
            if (!groupedData[item.time]) groupedData[item.time] = 0;
            groupedData[item.time] += item.likes;
        });
    }

    // 데이터가 하나도 없으면 0초부터 시작하는 빈 그래프라도 보여줌
    const labels = Object.keys(groupedData).length ? Object.keys(groupedData).sort((a, b) => a - b) : ['0'];
    const likeCounts = Object.keys(groupedData).length ? labels.map(t => groupedData[t]) : [0];

    const displayLabels = labels.map(seconds => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s.toString().padStart(2, '0')}`;
    });

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: displayLabels,
            datasets: [{
                label: '🔥 질문 공감도',
                data: likeCounts,
                borderColor: '#ff6384',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { display: false }, ticks: { stepSize: 1 } }, // 정수로만 표시
                x: { grid: { display: false } }
            },
            onClick: (e, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const seconds = labels[index];
                    seekTo(seconds);
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const csrftoken = getCookie('csrftoken');

    // 그래프 데이터 로드 및 실행
    const dataScript = document.getElementById('graph-data');
    if (dataScript) {
        try {
            const graphData = JSON.parse(dataScript.textContent);
            drawEmpathyGraph(graphData);
        } catch (e) {
            console.error("그래프 데이터 파싱 실패", e);
        }
    }

    // 1. 댓글 등록
    const commentSubmitBtn = document.getElementById('comment-submit-btn');
    if (commentSubmitBtn) {
        commentSubmitBtn.addEventListener('click', function() {
            const content = document.getElementById('comment-content').value;
            let timetag = document.getElementById('comment-timetag').value;
            const imageFile = document.getElementById('comment-image').files[0];
            const video = document.getElementById('lecture');
            const pageContainer = document.querySelector('.page-container');

            if (timetag == 0 || timetag == "" || timetag == "0") {
                timetag = Math.floor(video.currentTime);
            }

            if (!content.trim()) {
                alert('내용을 입력해주세요');
                return;
            }

            // HTML에 적어둔 data-comment-create-url 사용
            const targetUrl = pageContainer.dataset.commentCreateUrl;

            const formData = new FormData();
            formData.append('content', content);
            formData.append('timetag', timetag);
            if (imageFile) formData.append('image', imageFile);

            fetch(targetUrl, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') location.reload();
                else alert('등록 실패');
            });
        });
    }

    // 2. 좋아요 (URL을 HTML data 속성에서 가져옴)
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetUrl = this.dataset.url; // 여기서 HTML의 data-url을 읽음
            
            fetch(targetUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    this.querySelector('.like-count').textContent = data.like_count;
                }
            });
        });
    });

    // 3. 대댓글 등록
    document.querySelectorAll('.reply-submit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const targetUrl = this.dataset.url; // HTML의 data-url 읽음
            const inputField = document.querySelector(`input[data-reply-input-id="${commentId}"]`);
            const content = inputField ? inputField.value : '';

            if (!content.trim()) {
                alert('내용을 입력해주세요');
                return;
            }

            const formData = new FormData();
            formData.append('content', content);

            fetch(targetUrl, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') location.reload();
                else alert('등록 실패');
            });
        });
    });

    // 4. 답글 토글
    document.querySelectorAll('.reply-toggle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const replyArea = document.querySelector(`.reply-area[data-reply-id="${commentId}"]`);
            if (replyArea) {
                replyArea.style.display = (replyArea.style.display === 'none') ? 'block' : 'none';
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}