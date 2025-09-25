document.addEventListener('DOMContentLoaded', function() {
    const sidebarLinks = document.querySelectorAll('.sidebar ul li a');
    const currentURL = window.location.href;

    sidebarLinks.forEach(link => {
        if (link.href === currentURL) {
            link.classList.add('active');
        }
    });
});

const ctx = document.getElementById('barchart');

new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat','Sun'],
    datasets: [{
      label: '# of Subscribers',
      data: [7, 4, 2, 3, 1, 6,2],
      borderWidth: 1,
      backgroundColor:'#e50ebe',
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

const progressBar = document.querySelector('.progress-bar');
const percentText = document.querySelector('.progress-text');

const progress = progressBar.dataset.percent;
const progressAngle = (progress / 100) * 360; // Calculate progress angle

progressBar.style.transform = `rotate(-${progressAngle}deg)`;
percentText.textContent = `${progress}%`; // Set the text content

