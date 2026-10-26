"use strict";
(function () {
    var sections = document.querySelectorAll("section[id]");
    var items = document.querySelectorAll(".rail__item");
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            var _a;
            if (entry.isIntersecting) {
                items.forEach(function (item) { return item.classList.remove("rail__item--active"); });
                var link = document.querySelector('.rail__item a[href="#' + entry.target.id + '"]');
                (_a = link === null || link === void 0 ? void 0 : link.closest(".rail__item")) === null || _a === void 0 ? void 0 : _a.classList.add("rail__item--active");
            }
        });
    }, { rootMargin: "-20% 0px -70% 0px" });
    sections.forEach(function (section) { return observer.observe(section); });
})();
