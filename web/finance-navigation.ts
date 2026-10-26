(function () {
  const sections = document.querySelectorAll("section[id]");
  const items = document.querySelectorAll(".rail__item");
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        items.forEach(item => item.classList.remove("rail__item--active"));
        const link = document.querySelector('.rail__item a[href="#' + entry.target.id + '"]');
        link?.closest(".rail__item")?.classList.add("rail__item--active");
      }
    });
  }, { rootMargin: "-20% 0px -70% 0px" });
  sections.forEach(section => observer.observe(section));
})();
