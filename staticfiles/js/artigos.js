// Modal logic for artigos page
(function() {
  document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById('article-modal');
    var btn = document.getElementById('add-article-btn');
    var closeBtn = document.getElementById('close-article-modal');
    if (btn && modal && closeBtn) {
      btn.addEventListener('click', function(e) {
        // Only open modal if not inside a form submit
        if (e.target === btn || btn.contains(e.target)) {
          e.stopPropagation();
          e.preventDefault();
          modal.style.display = 'flex';
        }
      });
      closeBtn.onclick = function() { modal.style.display = 'none'; };
      window.onclick = function(event) {
        if (event.target == modal) { modal.style.display = 'none'; }
      };
    }
  });
})();
