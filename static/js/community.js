// JS for opening/closing the community creation modal
(function() {
  const addBtn = document.getElementById('add-community-btn');
  const modal = document.getElementById('community-modal');
  const closeModal = document.getElementById('close-community-modal');
  if (addBtn && modal && closeModal) {
    addBtn.onclick = () => { modal.style.display = 'flex'; };
    closeModal.onclick = () => { modal.style.display = 'none'; };
    window.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };
  }
})();


