function seekTo(seconds) {
    const video = document.getElementById('lecture');
    video.currentTime = seconds;
    video.play();
}

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