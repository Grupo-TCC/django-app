function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("click", function (e) {
  const btn = e.target.closest(".follow-btn");
  if (!btn) return;

  const url = btn.dataset.url;
  const csrftoken = getCookie("csrftoken");

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        if (data.is_following) {
          btn.classList.add("following");
          btn.textContent = "Deixar de Seguir";

          // Adiciona o usuário seguido na lista "Pessoas que você segue"
          const seguindoLista = document.querySelector(".seguindo-lista");
          if (seguindoLista && !document.getElementById("seguindo-" + data.user.id)) {
            // Remove mensagem "Você ainda não segue ninguém."
            const emptyMsg = seguindoLista.querySelector("p");
            if (emptyMsg && emptyMsg.textContent.includes("não segue ninguém")) {
              emptyMsg.remove();
            }
            // Cria o elemento do usuário seguido, incluindo o botão de deixar de seguir
            const div = document.createElement("div");
            div.className = "seguindo-item";
            div.id = "seguindo-" + data.user.id;
            div.innerHTML = `
              <img src="${data.user.profile_picture_url}">
              <p>${data.user.fullname}</p>
              <button type="button" class="seguir-link follow-btn following" data-url="/feed/follow/${data.user.id}/">Deixar de Seguir</button>
            `;
            seguindoLista.appendChild(div);
          }

          // Remove o usuário das sugestões
          const sugestaoCard = btn.closest(".sugestao-card");
          if (sugestaoCard) sugestaoCard.remove();
        } else {
          btn.classList.remove("following");
          btn.textContent = "Seguir";
          // Remove da lista de seguidos
          const seguido = document.getElementById("seguindo-" + data.user.id);
          if (seguido) seguido.remove();
          // Se não houver mais seguidos, mostra mensagem
          const seguindoLista = document.querySelector(".seguindo-lista");
          if (seguindoLista && seguindoLista.querySelectorAll(".seguindo-item").length === 0) {
            const p = document.createElement("p");
            p.textContent = "Você ainda não segue ninguém.";
            seguindoLista.appendChild(p);
          }

          // Re-adiciona o usuário às sugestões
          const sugestoesGrid = document.querySelector(".sugestoes-grid");
          if (sugestoesGrid && !document.getElementById("sugestao-" + data.user.id)) {
            const card = document.createElement("div");
            card.className = "sugestao-card";
            card.id = "sugestao-" + data.user.id;
            card.innerHTML = `
              <img src="${data.user.profile_picture_url}">
              <h4>${data.user.fullname}</h4>
              <p>Leitor</p>
              <button type="button" class="seguir-link follow-btn" data-url="/feed/follow/${data.user.id}/">Seguir</button>
            `;
            sugestoesGrid.appendChild(card);
          }
        }
      }
    });
});
