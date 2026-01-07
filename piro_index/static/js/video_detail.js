// ----여기부터 시현 -----

function drawEmpathyGraph(data) {
    const ctx = document.getElementById('questionChart').getContext('2d');

    // 1. 같은 시간에 여러 질문이 있을 수 있으니, 시간별로 공감수를 합산합니다.
    const groupedData = {};
    data.forEach(item => {
        if (!groupedData[item.time]) {
            groupedData[item.time] = 0;
        }
        groupedData[item.time] += item.likes; // 공감수를 더함
    });

    // 2. 차트용 라벨(시간)과 데이터(공감수 합계) 추출 및 정렬
    const labels = Object.keys(groupedData).sort((a, b) => a - b);
    const likeCounts = labels.map(time => groupedData[time]);

    // 3. 그래프 그리기
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.map(t => t + 's'),
            datasets: [{
                label: '🔥 저도 궁금해요(공감 수)',
                data: likeCounts,
                borderColor: '#ff6384', // 공감이니까 따뜻한 색으로!
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    seekTo(labels[index]); // 클릭 시 해당 시간으로 이동은 동일!
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: '공감 수' }
                }
            }
        }
    });
}
function seekTo(seconds, element) {
    // 1. 영상 이동 로직
    const video = document.getElementById('lecture');
    video.currentTime = seconds;
    video.play();

    // 2. [핵심] 색상 유지 로직
    // (1) 일단 모든 index_content에서 'selected' 클래스를 제거합니다.
    const allItems = document.querySelectorAll('.index_content');
    allItems.forEach(item => {
        item.classList.remove('selected');
    });

    // (2) 내가 방금 클릭한 그 요소(element)에만 'selected' 클래스를 붙입니다.
    if (element) {
        element.classList.add('selected');
    }
}

// ----여기까지 시현-----




// ====여기부터 선우====
// ========================================
// 1. 댓글 등록
// ========================================
document.getElementById('comment-submit-btn').addEventListener('click', function() {
    const content = document.getElementById('comment-content').value;
    const timetag = document.getElementById('comment-timetag').value;
    const imageFile = document.getElementById('comment-image').files[0];
    
    if (!content.trim()) {
        alert('내용을 입력해주세요');
        return;
    }
    
    const formData = new FormData();
    formData.append('content', content);
    formData.append('timetag', timetag);
    if (imageFile) {
        formData.append('image', imageFile);
    }
    
    // video_pk는 HTML에서 전달받아야 함 (예: data-video-id)
    const videoPk = document.querySelector('[data-video-id]').dataset.videoId;
    
    fetch(`/video/${videoPk}/comment/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload(); // 새로고침해서 댓글 목록 업데이트
        }
    })
    .catch(error => console.error('Error:', error));
});


// ========================================
// 2. 답글 등록
// ========================================
document.querySelectorAll('.reply-submit-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const commentId = this.dataset.commentId;
        const content = document.querySelector(`[data-reply-input-id="${commentId}"] .reply-content`).value;
        
        if (!content.trim()) {
            alert('답글 내용을 입력해주세요');
            return;
        }
        
        const formData = new FormData();
        formData.append('content', content);
        
        fetch(`/comment/${commentId}/delete/`, {  // [수정] video -> comment 로 변경
            method: 'POST',
            headers: {
            'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); // 새로고침
            }
        })
        .catch(error => console.error('Error:', error));
    });
});


// ========================================
// 3. 좋아요 토글
// ========================================
document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const commentId = this.dataset.commentId;
        
        fetch(`/comment/${commentId}/like`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 좋아요 수 업데이트
                this.querySelector('.like-count').textContent = data.like_count;
            }
        })
        .catch(error => console.error('Error:', error));
    });
});


// ========================================
// 4. 답글 토글 (보기/숨기기)
// ========================================
document.querySelectorAll('.reply-toggle-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const commentId = this.dataset.commentId;
        const replyContainer = document.querySelector(`[data-reply-id="${commentId}"]`);
        
        if (replyContainer.style.display === 'none' || !replyContainer.style.display) {
            replyContainer.style.display = 'block';
        } else {
            replyContainer.style.display = 'none';
        }
    });
});


// ========================================
// 5. 사진 토글 (보기/숨기기)
// ========================================
document.querySelectorAll('.image-toggle-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const commentId = this.dataset.commentId;
        const imageContainer = document.querySelector(`[data-image-id="${commentId}"]`);
        
        if (imageContainer.style.display === 'none' || !imageContainer.style.display) {
            imageContainer.style.display = 'block';
        } else {
            imageContainer.style.display = 'none';
        }
    });
});


// ========================================
// 6. 답글 작성 인풋 토글
// ========================================
document.querySelectorAll('.reply-write-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const commentId = this.dataset.commentId;
        const inputContainer = document.querySelector(`[data-reply-input-id="${commentId}"]`);
        
        if (inputContainer.style.display === 'none' || !inputContainer.style.display) {
            inputContainer.style.display = 'block';
        } else {
            inputContainer.style.display = 'none';
        }
    });
});


// ========================================
// 7. 타임태그 클릭 시 영상 이동
// ========================================
document.querySelectorAll('.timetag').forEach(tag => {
    tag.addEventListener('click', function() {
        const seconds = parseInt(this.textContent);
        seekTo(seconds); // 기존 함수 재사용
    });
});


// ========================================
// 8. 댓글 삭제 (운영진만)
// ========================================
document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (!confirm('정말 삭제하시겠습니까?')) {
            return;
        }
        
        const commentId = this.dataset.commentId;
        
        fetch(`/video/${commentId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById(`comment-${commentId}`).remove();
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});


// ========================================
// 유틸리티: CSRF 토큰 가져오기
// ========================================
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

// =====여기까지 선우=====