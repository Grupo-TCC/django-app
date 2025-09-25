// Search logic for all pages with search component
(function() {
  document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const searchForm = document.getElementById("search-form");
    const searchSpinner = document.getElementById("search-spinner");

    if (searchForm) {
      searchForm.addEventListener("submit", function (e) {
        e.preventDefault();
        e.stopPropagation();
        
        const searchTerm = searchInput.value.trim();
        const url = new URL(window.location.href);
        
        // Show loading spinner
        if (searchSpinner) {
          searchSpinner.style.display = 'inline-block';
        }
        
        if (searchTerm) {
          url.searchParams.set('q', searchTerm);
        } else {
          url.searchParams.delete('q');
        }
        
        // Remove other search parameters to start fresh
        url.searchParams.delete('search_type');
        
        // Add page-specific search type
        const searchType = getSearchTypeForPage();
        if (searchType) {
          url.searchParams.set('search_type', searchType);
        }
        
        // Redirect to new URL
        setTimeout(() => {
          window.location.href = url.toString();
        }, 300);
      });
    }

    // Function to determine search type based on current page
    function getSearchTypeForPage() {
      const currentPath = window.location.pathname;
      
      if (currentPath.includes('/conexao/') || currentPath.includes('/conexoes/')) {
        return 'name_only'; // Search only by name for conexao page
      } else if (currentPath.includes('/artigos/') || currentPath.includes('/artigo/')) {
        return 'multiple_fields'; // Search by name, title, research area for artigos
      } else if (currentPath.includes('/pesquisadores/')) {
        return 'researcher_fields'; // Search by name, institution, expertise
      }
      
      return 'default'; // Fallback to default search
    }

    // Preserve search term on page load
    if (searchInput) {
      const urlParams = new URLSearchParams(window.location.search);
      const searchQuery = urlParams.get('q');
      if (searchQuery) {
        searchInput.value = searchQuery;
      }
    }
  });
})();