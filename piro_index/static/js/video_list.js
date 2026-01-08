// video_list.js - 비디오 리스트 JavaScript

// CSRF 토큰 가져오기
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

const csrftoken = getCookie('csrftoken');

// 페이지 로드 시 이벤트 등록
document.addEventListener('DOMContentLoaded', function() {
    // 모든 찜하기 아이콘에 클릭 이벤트 등록
    document.querySelectorAll('.logo-icon').forEach(function(logo) {
        logo.addEventListener('click', function() {
            const videoId = this.getAttribute('data-video-id');
            toggleSave(videoId, this);
        });
    });
});

// 찜하기 토글 함수
function toggleSave(videoId, logoElement) {
    fetch(`/video/${videoId}/save/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.is_saved) {
                // 찜한 상태로 변경
                logoElement.classList.remove('unsaved');
                logoElement.classList.add('saved');
            } else {
                // 찜하지 않은 상태로 변경
                logoElement.classList.remove('saved');
                logoElement.classList.add('unsaved');
            }
            
            // 토스트 메시지 표시
            showToast(data.message);
        } else {
            // 에러 처리
            alert(data.message || '오류가 발생했습니다.');
            if (data.message && data.message.includes('로그인')) {
                window.location.href = '/';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('찜하기 처리 중 오류가 발생했습니다.');
    });
}

// 토스트 메시지 표시
function showToast(message) {
    // 기존 토스트 제거
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        document.body.removeChild(existingToast);
    }
    
    // 새 토스트 생성
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // 애니메이션
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // 자동 숨김
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 400);
    }, 2500);
}